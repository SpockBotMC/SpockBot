"""
Interact with the world:
- swing the arm, sneak, sprint, jump with a horse, leave the bed
- look around
- dig/place/use blocks
- use the held (active) item
- use/attack entities
- steer vehicles
- place and write signs
- edit and sign books

By default, the client sends swing and look packets like the vanilla client.
This can be disabled by setting the ``auto_swing`` and ``auto_look`` flags.
"""
import math

from spockbot.mcdata import constants
from spockbot.mcp import nbt
from spockbot.mcp.proto import MC_SLOT
from spockbot.plugins.base import PluginBase, pl_announce
from spockbot.plugins.tools.event import EVENT_UNREGISTER
from spockbot.vector import Vector3


@pl_announce('Interact')
class InteractPlugin(PluginBase):
    requires = ('ClientInfo', 'Event', 'Inventory', 'Net', 'Channels')

    def __init__(self, ploader, settings):
        super(InteractPlugin, self).__init__(ploader, settings)
        ploader.provides('Interact', self)

        self.sneaking = False
        self.sprinting = False
        self.dig_pos_dict = {'x': 0, 'y': 0, 'z': 0}

        self.auto_swing = True  # move arm when clicking
        self.auto_look = True  # look at clicked things

    def swing_arm(self):
        self.net.push_packet('PLAY>Animation', {})

    def _entity_action(self, action, jump_boost=100):
        entity_id = self.clientinfo.eid
        self.net.push_packet('PLAY>Entity Action', {
            'eid': entity_id,
            'action': action,
            'jump_boost': jump_boost,
        })

    def leave_bed(self):
        self._entity_action(constants.ENTITY_ACTION_LEAVE_BED)

    def sneak(self, sneak=True):
        self._entity_action(constants.ENTITY_ACTION_SNEAK
                            if sneak else constants.ENTITY_ACTION_UNSNEAK)
        self.sneaking = sneak

    def unsneak(self):
        self.sneak(False)

    def sprint(self, sprint=True):
        self._entity_action(constants.ENTITY_ACTION_START_SPRINT if sprint
                            else constants.ENTITY_ACTION_STOP_SPRINT)
        self.sprinting = sprint

    def unsprint(self):
        self.sprint(False)

    def jump_horse(self, jump_boost=100):
        self._entity_action(constants.ENTITY_ACTION_JUMP_HORSE, jump_boost)

    def open_inventory(self):
        self._entity_action(constants.ENTITY_ACTION_OPEN_INVENTORY)

    def look(self, yaw=0.0, pitch=0.0, radians=False):
        if radians:
            self.clientinfo.position.yaw = math.degrees(yaw)
            self.clientinfo.position.pitch = math.degrees(pitch)
        else:
            self.clientinfo.position.yaw = yaw
            self.clientinfo.position.pitch = pitch

    def look_rel(self, d_yaw=0.0, d_pitch=0.0, radians=False):
        self.look(self.clientinfo.position.yaw + d_yaw,
                  self.clientinfo.position.pitch + d_pitch,
                  radians=radians)

    def look_at_rel(self, delta):
        self.look(*delta.yaw_pitch)

    def look_at(self, pos):
        delta = Vector3(pos) - self.clientinfo.eye_pos
        if delta.x or delta.z:
            self.look_at_rel(delta)
        else:  # looking up or down, do not turn head
            self.look(self.clientinfo.position.yaw, delta.yaw_pitch.pitch)

    def _send_dig_block(self, status, pos=None, face=constants.FACE_TOP):
        if status == constants.DIG_START:
            self.dig_pos_dict = pos.floor().get_dict().copy()
        self.net.push_packet('PLAY>Player Digging', {
            'status': status,
            'location': self.dig_pos_dict,
            'face': face,
        })

    def start_digging(self, pos, face=constants.FACE_TOP):
        pos = Vector3(pos)
        if self.auto_look:
            self.look_at(pos.floor() + Vector3(0.5, 0.5, 0.5))
        self._send_dig_block(status=constants.DIG_START, pos=pos, face=face)
        if self.auto_swing:
            self.swing_arm()
            # TODO send swing animation until done or stopped

    def cancel_digging(self):
        self._send_dig_block(status=constants.DIG_CANCEL)

    def finish_digging(self):
        self._send_dig_block(status=constants.DIG_FINISH)

    def dig_block(self, pos):
        """
        Not cancelable.
        """
        self.start_digging(pos)
        self.finish_digging()

    def _send_click_block(self, pos, face=constants.FACE_TOP,
                          cursor_pos=Vector3(8, 8, 8)):
        self.net.push_packet('PLAY>Player Block Placement', {
            'location': pos.floor().get_dict(),
            'direction': face,
            'held_item': self.inventory.active_slot.get_dict(),
            'cur_pos_x': int(cursor_pos.x),
            'cur_pos_y': int(cursor_pos.y),
            'cur_pos_z': int(cursor_pos.z),
        })

    def click_block(self, pos, look_at_block=True, swing=True, **kwargs):
        """
        Click on a block.
        Examples: push button, open window, make redstone ore glow

        Args:
            face (int): side of the block on which the block is placed on
            cursor_pos (Vector3): where to click inside the block,
                each dimension 0-15
        """
        pos = Vector3(pos)
        if look_at_block and self.auto_look:
            # TODO look at cursor_pos
            self.look_at(pos.floor() + Vector3(0.5, 0.5, 0.5))
        self._send_click_block(pos, **kwargs)
        if swing and self.auto_swing:
            self.swing_arm()

    def place_block(self, pos, sneak=True, **kwargs):
        """
        Place a block next to ``pos``.
        If the block at ``pos`` is air, place at ``pos``.
        """
        sneaking_before = self.sneaking
        if sneak:
            self.sneak()
        self.click_block(pos, **kwargs)
        if not sneaking_before:
            self.sneak(sneaking_before)

    def use_bucket(self, pos):  # TODO
        """
        Using buckets is different from placing blocks.
        See "Special note on using buckets"
        in http://wiki.vg/Protocol#Player_Block_Placement
        """
        raise NotImplementedError(self.use_bucket.__doc__)

    def place_sign(self, pos, lines=[], **place_block_kwargs):
        """
        Place a sign block and write on it.
        """
        if self.inventory.active_slot.item_id != 323:
            raise ValueError('Must hold sign to place, not "%s"'
                             % self.inventory.active_slot.item)

        def write_sign_text(event, packet):
            data = {'location': packet.data['location']}
            for i in range(4):
                data['line_%i' % (i + 1)] = lines[i] if i < len(lines) else ''

            self.net.push_packet('PLAY>Update Sign', data)
            return EVENT_UNREGISTER

        self.event.reg_event_handler('PLAY<Sign Editor Open', write_sign_text)
        self.place_block(pos, **place_block_kwargs)

    def activate_item(self):
        """
        Use (hold right-click) the item in the active slot.
        Examples: pull the bow, start eating once, throw an egg.
        """
        self._send_click_block(pos=Vector3(-1, 255, -1),
                               face=-1,
                               cursor_pos=Vector3(-1, -1, -1))

    def deactivate_item(self):
        """
        Stop using (release right-click) the item in the active slot.
        Examples: shoot the bow, stop eating.
        """
        self._send_dig_block(constants.DIG_DEACTIVATE_ITEM)

    def use_entity(self, entity, cursor_pos=None,
                   action=constants.INTERACT_ENTITY):
        """
        Uses (right-click) an entity to open its window.
        Setting ``cursor_pos`` sets ``action`` to "interact at".
        """
        if self.auto_look:
            self.look_at(Vector3(entity))  # TODO look at cursor_pos

        if cursor_pos is not None and action == constants.INTERACT_ENTITY:
            action = constants.INTERACT_ENTITY_AT

        packet = {'target': entity.eid, 'action': action}
        if action == constants.INTERACT_ENTITY_AT:
            packet['target_x'] = cursor_pos.x
            packet['target_y'] = cursor_pos.y
            packet['target_z'] = cursor_pos.z
        self.net.push_packet('PLAY>Use Entity', packet)

        if self.auto_swing and action == constants.ATTACK_ENTITY:
            self.swing_arm()

    def attack_entity(self, entity):
        self.use_entity(entity, action=constants.ATTACK_ENTITY)

    def mount_vehicle(self, entity):
        self.use_entity(entity)

    def steer_vehicle(self, left=0.0, forward=0.0,
                      jump=False, unmount=False):
        flags = 0
        if jump:
            flags += 1
        if unmount:
            flags += 2
        self.net.push_packet('PLAY>Steer Vehicle', {
            'sideways': left,
            'forward': forward,
            'flags': flags,
        })

    def unmount_vehicle(self):
        self.steer_vehicle(unmount=True)

    def jump_vehicle(self):
        self.steer_vehicle(jump=True)

    def write_book(self, text, author="", title="", sign=False):
        """Write text to the current book in hand, optionally sign the book"""
        book = self._setup_book()
        if book is None:
            return False
        pages = (text[0+i:constants.BOOK_CHARS_PER_PAGE+i]
                 for i in range(0, len(text), constants.BOOK_CHARS_PER_PAGE))
        self.edit_book(pages)
        if sign:
            self.sign_book(author, title)

    def edit_book(self, pages):
        """Set the pages of current book in hand"""
        book = self._setup_book()
        if book is None:
            return False
        nbtpages = nbt.TagList(nbt.TagString)
        for i, page in enumerate(pages):
            if i >= constants.BOOK_MAXPAGES:
                break
            nbtpages.insert(i, nbt.TagString(page))
        book.nbt["pages"] = nbtpages
        self.channels.send("MC|BEdit", self._pack_book(book))

    def sign_book(self, author, title):
        """Sign current book in hand"""
        book = self._setup_book()
        if book is None:
            return False
        book.nbt["author"] = nbt.TagString(author)
        book.nbt["title"] = nbt.TagString(title)
        # TODO: don't use hard coded id
        book.item_id = 387  # written book
        self.channels.send("MC|BSign", self._pack_book(book))

    def _setup_book(self):
        book = self.inventory.active_slot
        # TODO: Dont use hard coded ID
        if book.item_id != 386:  # book and quill
            return None
        if book.nbt is None:
            book.nbt = nbt.TagCompound()
        return book

    def _pack_book(self, book):
        return self.channels.encode(((MC_SLOT, "slot"),),
                                    {"slot": book.get_dict()})
