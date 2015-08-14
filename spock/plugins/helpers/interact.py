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
import math

from spock.plugins.base import PluginBase
from spock.utils import pl_announce
from spock.vector import Vector3

PLAYER_HEIGHT = 1.74

INTERACT_ENTITY = 0
ATTACK_ENTITY = 1
INTERACT_ENTITY_AT = 2

ENTITY_ACTION_SNEAK = 0
ENTITY_ACTION_UNSNEAK = 1
ENTITY_ACTION_LEAVE_BED = 2
ENTITY_ACTION_START_SPRINT = 3
ENTITY_ACTION_STOP_SPRINT = 4
ENTITY_ACTION_JUMP_HORSE = 5
ENTITY_ACTION_OPEN_INVENTORY = 6

# the six faces of a block
FACE_Y_NEG = 0
FACE_Y_POS = 1
FACE_Z_NEG = 2
FACE_Z_POS = 3
FACE_X_NEG = 4
FACE_X_POS = 5

DIG_START = 0
DIG_CANCEL = 1
DIG_FINISH = 2
DIG_DROP_STACK = 3
DIG_DROP_ITEM = 4
DIG_DEACTIVATE_ITEM = 5


@pl_announce('Interact')
class InteractPlugin(PluginBase):
    requires = ('ClientInfo', 'Inventory', 'Net')

    def __init__(self, ploader, settings):
        super().__init__(ploader, settings)
        ploader.provides('Interact', self)

        self.sneaking = False
        self.sprinting = False
        self.auto_swing = True  # move arm when clicking
        self.auto_look = True  # look at clicked things

        self.dig_pos_dict = {'x': 0, 'y': 0, 'z': 0}

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
        self._entity_action(ENTITY_ACTION_LEAVE_BED)

    def sneak(self, sneak=True):
        self._entity_action(ENTITY_ACTION_SNEAK
                            if sneak else ENTITY_ACTION_UNSNEAK)
        self.sneaking = sneak

    def unsneak(self):
        self.sneak(False)

    def sprint(self, sprint=True):
        self._entity_action(ENTITY_ACTION_START_SPRINT
                            if sprint else ENTITY_ACTION_STOP_SPRINT)
        self.sprinting = sprint

    def unsprint(self):
        self.sprint(False)

    def jump_horse(self, jump_boost=100):
        self._entity_action(ENTITY_ACTION_JUMP_HORSE, jump_boost)

    def chat(self, message):
        self.net.push_packet('PLAY>Chat Message', {'message': message})

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

    def look_at(self, pos):
        # TODO use Vector3
        delta_x = pos.x - self.clientinfo.position.x
        delta_y = pos.y - self.clientinfo.position.y + PLAYER_HEIGHT
        delta_z = pos.z - self.clientinfo.position.z
        self.look_at_rel(Vector3(delta_x, delta_y, delta_z))

    def look_at_rel(self, delta):
        ground_distance = math.sqrt(delta.x * delta.x + delta.z * delta.z)
        pitch = math.atan2(delta.y, ground_distance) * 180 / math.pi
        yaw = math.atan2(-delta.x, -delta.z) * 180 / math.pi
        self.look(yaw, pitch)

    def _send_dig_block(self, status, pos=None, face=FACE_Y_POS):
        if status == DIG_START:
            self.dig_pos_dict = pos.get_dict().copy()
        self.net.push_packet('PLAY>Player Digging', {
            'status': status,
            'location': self.dig_pos_dict,
            'face': face,
        })

    def start_digging(self, pos):
        if self.auto_look:
            self.look_at(pos)  # TODO look at block center
        self._send_dig_block(DIG_START, pos)
        if self.auto_swing:
            self.swing_arm()
        # TODO send swing animation until done or stopped

    def cancel_digging(self):
        self._send_dig_block(DIG_CANCEL)

    def finish_digging(self):
        self._send_dig_block(DIG_FINISH)

    def dig_block(self, pos):
        """
        Not cancelable.
        """
        self.start_digging(pos)
        self.finish_digging()

    def click_block(self, pos, face=1, cursor_pos=Vector3(8, 8, 8),
                    look_at_block=True):
        """
        Click on a block.
        Examples: push button, open window, make redstone ore glow
        :param face: side of the block on which the block is placed on
        :param cursor_pos: where to click inside the block, each dimension 0-15
        """
        if look_at_block and self.auto_look:
            # TODO look at cursor_pos
            self.look_at(pos)
        self.net.push_packet('PLAY>Player Block Placement', {
            'location': pos.get_dict(),
            'direction': face,
            'held_item': self.inventory.active_slot.get_dict(),
            'cur_pos_x': int(cursor_pos.x),
            'cur_pos_y': int(cursor_pos.y),
            'cur_pos_z': int(cursor_pos.z),
        })
        if self.auto_swing:
            self.swing_arm()

    def place_block(self, pos, face=1, cursor_pos=Vector3(8, 8, 8),
                    look_at_block=True, sneak=True):
        """
        Place a block next to pos. If the block at pos is air, place at pos.
        """
        sneaking_before = self.sneaking
        if sneak:
            self.sneak()
        self.click_block(pos, face, cursor_pos, look_at_block)
        if sneak:
            self.sneak(sneaking_before)

    def use_bucket(self, pos):  # TODO
        """
        Using buckets is different from placing blocks.
        See "Special note on using buckets"
        in http://wiki.vg/Protocol#Player_Block_Placement
        """
        raise NotImplementedError

    def activate_item(self):
        """
        Use (hold right-click) the item in the active slot.
        Examples: pull the bow, start eating once, throw an egg.
        """
        self.click_block(Vector3(-1, 255, -1),
                         face=1,
                         cursor_pos=Vector3(-1, -1, -1),
                         look_at_block=False)

    def deactivate_item(self):
        """
        Stop using (release right-click) the item in the active slot.
        Examples: shoot the bow, stop eating.
        """
        self._send_dig_block(DIG_DEACTIVATE_ITEM)

    def use_entity(self, entity, cursor_pos=None, action=INTERACT_ENTITY):
        """
        Uses (right-click) an entity to open its window.
        Setting `cursor_pos` sets `action` to "interact at".
        """
        if self.auto_look:
            self.look_at(entity)  # TODO look at cursor_pos
        if cursor_pos is not None:
            action = INTERACT_ENTITY_AT
        packet = {'target': entity.eid, 'action': action}
        if action == INTERACT_ENTITY_AT:
            packet['target_x'] = cursor_pos.x
            packet['target_y'] = cursor_pos.y
            packet['target_z'] = cursor_pos.z
        self.net.push_packet('PLAY>Use Entity', packet)
        if self.auto_swing:
            self.swing_arm()

    def attack_entity(self, entity):
        self.use_entity(entity, action=ATTACK_ENTITY)

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
