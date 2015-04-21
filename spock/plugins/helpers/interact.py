"""
Interact with the world.
- swing the arm, sneak, sprint, jump with a horse, leave the bed
- chat, whisper (private message)
- look around
- dig/place/use blocks
- use the held (active) item
- use/attack entities
- steer vehicles
"""
import math
from spock.utils import pl_announce, Vec3

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
FACE_Z_NEG = 0
FACE_Z_POS = 1
FACE_X_NEG = 0
FACE_X_POS = 1

@pl_announce('Interact')
class InteractPlugin:
	def __init__(self, ploader, settings):
		self.clinfo = ploader.requires('Clientinfo')
		self.inventory = ploader.requires('Inventory')
		self.net = ploader.requires('Net')
		ploader.provides('Interact', self)

		self.sneaking = False
		self.noswing = False  # set to True to prevent arm movement

	def swing_arm(self):
		if not self.noswing:
			self.net.push_packet('PLAY>Animation', {})

	def _entity_action(self, action, jump_boost=100, entity_id=None):
		if entity_id is None:
			entity_id = self.clinfo.eid
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

	def unsprint(self):
		self.sprint(False)

	def jump_horse(self, jump_boost=100):
		self._entity_action(ENTITY_ACTION_JUMP_HORSE, jump_boost)

	def chat(self, message):
		self.net.push_packet('PLAY>Chat Message', {'message': message})

	def whisper(self, player, message):
		self.chat('/tell %s %s' % (player, message))

	def look(self, yaw=0, pitch=0):
		self.clinfo.position.pitch = pitch
		self.clinfo.position.yaw = yaw
		self.net.push_packet('PLAY>Player Look', {
			'yaw': yaw,
			'pitch': pitch,
			'on_ground': self.clinfo.position.on_ground
		})

	def look_relative(self, yaw=0, pitch=0):
		self.look_at(self.clinfo.position.yaw + yaw,
					 self.clinfo.position.pitch + pitch)

	def look_at(self, yaw=None, pitch=None, pos=None):
		if pos is not None:
			delta_x = pos.x - self.clinfo.position.x
			delta_y = pos.y - self.clinfo.position.y + 1.7  # player height
			delta_z = pos.z - self.clinfo.position.z
			groundDistance = math.sqrt(delta_x * delta_x + delta_z * delta_z)
			pitch = math.atan2(delta_y, groundDistance) * 180 / math.pi
			yaw = math.atan2(-delta_x, -delta_z) * 180 / math.pi
		self.look(yaw, pitch)

	def dig_block(self, coords):
		self.dig_coords_dict = coords.get_dict().copy()
		packet = {
			'status': 0,  # start
			'location': self.dig_coords_dict,
			'face': 1,
		}
		self.net.push_packet('PLAY>Player Digging', packet)

	def stop_digging(self):
		if not self.dig_coords_dict:
			# TODO raise or return?
			raise AssertionError('dig_block() must be called before stop_digging()')
		packet = {
			'status': 2,  # finish
			'location': self.dig_coords_dict,
			'face': 1,
		}
		self.net.push_packet('PLAY>Player Digging', packet)

	def place_block(self, coords, face=1, cursor_pos=Vec3(8,8,8)):
		"""
		Place a block next to coords, or
		at coords if the block at coords is air.
		"""
		sneaking_before = self.sneaking
		self.sneak()
		self.use_block(coords, face, cursor_pos)
		self.sneak(sneaking_before)

	def click_block(self, coords, face=1, cursor_pos=Vec3(8,8,8)):
		"""
		Click on a block, e.g. push button, open window, make redstone ore glow.
		:param face: side of the reference block on which the block is placed on
		:param cursor_pos: each dimension 0..15, where to click inside the block
		"""
		self.net.push_packet('PLAY>Player Block Placement', {
			'location': coords.get_dict(),
			'direction': face,
			'held_item': self.inventory.active_slot.get_dict(),
			'cur_pos_x': cursor_pos.x,
			'cur_pos_y': cursor_pos.y,
			'cur_pos_z': cursor_pos.z,
		})
		self.swing_arm()

	def activate_item(self):
		"""
		Use (hold right-click) the item in the active slot.
		Examples: pull the bow, start eating once, throw an egg.
		"""
		self.use_block(Vec3(-1, 255, -1), 1, Vec3(-1, -1, -1))

	def deactivate_item(self):
		"""
		Stop using (release right-click) the item in the active slot.
		Examples: shoot the bow, stop eating.
		"""
		self.net.push_packet('PLAY>Player Digging', {
			'status': 5,
			'location': Vec3(0, 0, 0).get_dict(),
			'face': 255,
		})

	def use_entity(self, entity_id, cursor_pos=Vec3(0.0, 0.0, 0.0), action=INTERACT_ENTITY):
		"""
		Uses (right-click) an entity to open its window.
		`action` is one of 0: interact, 1: attack, 2: interact at
		"""
		packet = {'target': entity_id, 'action': action}
		if action == INTERACT_ENTITY_AT:
			packet['target_x'] = cursor_pos.x
			packet['target_y'] = cursor_pos.y
			packet['target_z'] = cursor_pos.z
		self.net.push_packet('PLAY>Use Entity', packet)
		self.swing_arm()

	def attack_entity(self, entity_id):
		self.use_entity(entity_id, action=ATTACK_ENTITY)

	def mount_vehicle(self, entity_id):
		self.use_entity(entity_id)

	def steer_vehicle(self, sideways=0.0, forward=0.0, jump=False, unmount=False):
		flags = 0
		if jump: flags += 1
		if unmount: flags += 2
		packet = {
			'sideways': sideways,
			'forward': forward,
			'flags': flags,
		}
		self.net.push_packet('PLAY>Steer Vehicle', packet)

	def unmount_vehicle(self):
		self.steer_vehicle(unmount=True)

	def jump_vehicle(self):
		self.steer_vehicle(jump=True)
