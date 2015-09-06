"""
Interact with the world:
- swing the arm, sneak, sprint, jump with a horse, leave the bed
- chat, whisper (private message)
- look around
- dig/place/use blocks
- use the held (active) item
- use/attack entities
- steer vehicles

By default, the client sends swing and look packets like the vanilla client.
This can be disabled by setting the auto_swing and auto_look flags.
"""
from spock.mcdata import constants
from spock.plugins.base import PluginBase
from spock.utils import pl_announce
from spock.vector import Vector3


@pl_announce('Interact')
class InteractPlugin(PluginBase):
    requires = ('ClientInfo', 'Inventory', 'Net')

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

    def chat(self, message):
        while message:
            msg_part, message = message[:100], message[100:]
            self.net.push_packet('PLAY>Chat Message', {'message': msg_part})

    def whisper(self, player, message):
        self.chat('/tell %s %s' % (player, message))

    def look(self, yaw=0.0, pitch=0.0):
        """
        Turn the head. Both angles are in degrees.
        """
        self.clientinfo.position.pitch = pitch
        self.clientinfo.position.yaw = yaw
        self.net.push_packet('PLAY>Player Look', {
            'yaw': int(yaw),
            'pitch': int(pitch),
            'on_ground': self.clientinfo.position.on_ground
        })

    def look_rel(self, d_yaw=0.0, d_pitch=0.0):
        self.look(self.clientinfo.position.yaw + d_yaw,
                  self.clientinfo.position.pitch + d_pitch)

    def look_at_rel(self, delta):
        self.look(*delta.yaw_pitch)

    def look_at(self, pos):
        delta = pos - self.clientinfo.position
        delta.y -= constants.PLAYER_HEIGHT
        self.look_at_rel(delta)

    def _send_dig_block(self, status, pos=None, face=constants.FACE_Y_POS):
        if status == constants.DIG_START:
            self.dig_pos_dict = pos.get_dict().copy()
        self.net.push_packet('PLAY>Player Digging', {
            'status': status,
            'location': self.dig_pos_dict,
            'face': face,
        })

    def start_digging(self, pos):
        if self.auto_look:
            self.look_at(pos)  # TODO look at block center
        self._send_dig_block(constants.DIG_START, pos)
        if self.auto_swing:
            self.swing_arm()
            # TODO send swing animation until done or stopped

    def cancel_digging(self):
        self._send_dig_block(constants.DIG_CANCEL)

    def finish_digging(self):
        self._send_dig_block(constants.DIG_FINISH)

    def dig_block(self, pos):
        """
        Not cancelable.
        """
        self.start_digging(pos)
        self.finish_digging()

    def _send_click_block(self, pos, face=1, cursor_pos=Vector3(8, 8, 8)):
        self.net.push_packet('PLAY>Player Block Placement', {
            'location': pos.get_dict(),
            'direction': face,
            'held_item': self.inventory.active_slot.get_dict(),
            'cur_pos_x': int(cursor_pos.x),
            'cur_pos_y': int(cursor_pos.y),
            'cur_pos_z': int(cursor_pos.z),
        })

    def click_block(self, pos, face=1, cursor_pos=Vector3(8, 8, 8),
                    look_at_block=True, swing=True):
        """
        Click on a block.
        Examples: push button, open window, make redstone ore glow
        :param face: side of the block on which the block is placed on
        :param cursor_pos: where to click inside the block, each dimension 0-15
        """
        if look_at_block and self.auto_look:
            # TODO look at cursor_pos
            self.look_at(pos)
        self._send_click_block(pos, face, cursor_pos)
        if swing and self.auto_swing:
            self.swing_arm()

    def place_block(self, pos, face=1, cursor_pos=Vector3(8, 8, 8),
                    sneak=True, look_at_block=True, swing=True):
        """
        Place a block next to pos. If the block at pos is air, place at pos.
        """
        sneaking_before = self.sneaking
        if sneak:
            self.sneak()
        self.click_block(pos, face, cursor_pos, look_at_block, swing)
        if sneak:
            self.sneak(sneaking_before)

    def use_bucket(self, pos):  # TODO
        """
        Using buckets is different from placing blocks.
        See "Special note on using buckets"
        in http://wiki.vg/Protocol#Player_Block_Placement
        """
        raise NotImplementedError(self.use_bucket.__doc__)

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
        Setting `cursor_pos` sets `action` to "interact at".
        """
        if self.auto_look:
            self.look_at(Vector3(entity))  # TODO look at cursor_pos
        if cursor_pos is not None:
            action = constants.INTERACT_ENTITY_AT
        packet = {'target': entity.eid, 'action': action}
        if action == constants.INTERACT_ENTITY_AT:
            packet['target_x'] = cursor_pos.x
            packet['target_y'] = cursor_pos.y
            packet['target_z'] = cursor_pos.z
        self.net.push_packet('PLAY>Use Entity', packet)
        if self.auto_swing:
            self.swing_arm()

    def attack_entity(self, entity):
        self.use_entity(entity, action=constants.ATTACK_ENTITY)

    def mount_vehicle(self, entity):
        self.use_entity(entity)

    def steer_vehicle(self, sideways=0.0, forward=0.0,
                      jump=False, unmount=False):
        flags = 0
        if jump:
            flags += 1
        if unmount:
            flags += 2
        self.net.push_packet('PLAY>Steer Vehicle', {
            'sideways': sideways,
            'forward': forward,
            'flags': flags,
        })

    def unmount_vehicle(self):
        self.steer_vehicle(unmount=True)

    def jump_vehicle(self):
        self.steer_vehicle(jump=True)
