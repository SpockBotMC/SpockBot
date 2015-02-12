"""
The Inventory plugin keeps track of open windows and their slots.
It offers convenient methods to interact with open windows.
"""

from collections import deque
from spock.utils import pl_announce

import logging
logger = logging.getLogger('spock')

INV_BUTTON_LEFT = 0
INV_BUTTON_RIGHT = 1
INV_BUTTON_MIDDLE = 2

INV_MODE_CLICK = 0
INV_MODE_SHIFT = 1
INV_MODE_SWAP_HOTBAR = 2
INV_MODE_MIDDLE = 3
INV_MODE_DROP = 4
INV_MODE_PAINT = 5
INV_MODE_DOUBLECLICK = 6

INV_WINID_PLAYER = 0  # main inventory window ID, always open

class Slot:
	def __init__(self, id=-1, amount=0, damage=0, enchants=None):
		# ID == -1 means empty slot
		self.item_id = id
		self.amount = amount
		self.damage = damage
		# dict of ench_id -> ench_level
		self.enchants = enchants

	def get_as_packet_data(self):
		""" Formats the slot for network packing.
		Usually not needed because of the server-side inventory,
		sending {'id': -1} is sufficient. """
		data = {'id': self.item_id, 'amount': self.amount, 'damage': self.damage}
		if self.enchants is not None:
			data['enchants'] = self.enchants
		return data

inv_types = {}
def map_window_type(inv_type_id):
	def inner(cl):
		inv_types[inv_type_id] = cl
		cl.inv_type = inv_type_id
		return cl
	return inner

class InventoryBase:
	""" Base class for all inventory types. """

	def __init__(self, inv_type, window_id, title, slot_count):
		self.inv_type = inv_type  # unused
		self.window_id = window_id
		self.title = title
		self.slots = [Slot()] * slot_count
		self.properties = {}

# no @map_window_type(), because not opened/closed/updated by the server
class InventoryPlayer(InventoryBase):
	name = 'Inventory'

	def __init__(self):
		super().__init__(-1, INV_WINID_PLAYER, 'Inventory', 45)

	def craft_result_slot(self):
		return self.slots[0]

	def craft_grid_slots(self):
		return self.slots[1:5]

	def armor_slots(self):
		return self.slots[5:9]

	def inventory_slots(self):
		return self.slots[9:36]

	def hotbar_slots(self):
		return self.slots[36:45]

@map_window_type('minecraft:chest')
class InventoryChest(InventoryBase):
	""" Small, large, and glitched-out superlarge chests. """

	name = 'Chest'

@map_window_type('minecraft:crafting_table')
class InventoryWorkbench(InventoryBase):
	name = 'Workbench'

	def craft_result_slot(self):
		return self.slots[0]

	def craft_grid_slots(self):
		return self.slots[1:10]

@map_window_type('minecraft:furnace')
class InventoryFurnace(InventoryBase):
	name = 'Furnace'

	def smelted_slot(self):
		return self.slots[0]

	def fuel_slot(self):
		return self.slots[1]

	def result_slot(self):
		return self.slots[2]

	def progress_prop(self):
		return self.properties[0]

	def fuel_time_prop(self):
		return self.properties[1]

@map_window_type('minecraft:dispenser')
class InventoryDispenser(InventoryBase):
	name = 'Dispenser'

@map_window_type('minecraft:enchanting_table')
class InventoryEnchant(InventoryBase):
	name = 'Encantment Table'

	def enchanted_slot(self):
		return self.slots[0]

	def lapis_slot(self):
		return self.slots[1]

	# TODO how does selecting the enchantment work?

@map_window_type('minecraft:brewing_stand')
class InventoryBrewing(InventoryBase):
	name = 'Brewing Stand'

	def ingredient_slot(self):
		return self.slots[0]

	def result_slots(self):
		return self.slots[1:4]

	def brew_time_prop(self):
		return self.properties[0]

@map_window_type('minecraft:villager')
class InventoryVillager(InventoryBase):
	name = 'NPC Trade'

# TODO NPC slot getters

@map_window_type('minecraft:beacon')
class InventoryBeacon(InventoryBase):
	name = 'Beacon'

	def input_slot(self):
		return self.slots[0]

	def level_prop(self):
		return self.properties[0]

	def effect_one_prop(self):
		return self.properties[1]

	def effect_two_prop(self):
		return self.properties[2]

@map_window_type('minecraft:anvil')
class InventoryAnvil(InventoryBase):
	name = 'Anvil'

# TODO anvil slot getters

	def max_cost_prop(self):
		return self.properties[0]

@map_window_type('minecraft:hopper')
class InventoryHopper(InventoryBase):
	name = 'Hopper'

@map_window_type('minecraft:dropper')
class InventoryDropper(InventoryBase):
	name = 'Dropper'

@map_window_type('EntityHorse')
class InventoryHorse(InventoryBase):
	name = 'Horse'

	def __init__(self, eid=0, **args):
		super().__init__(**args)
		self.horse_entity_id = eid

	# TODO horse slot getters

class InventoryCore:
	""" Handles the player inventory and the last opened window. """

	def __init__(self, net, send_click):
		self.net = net
		self._send_click = send_click  # method to queue a click action
		self.selected_slot = 0
		# initialize main inventory, always open, always same ID
		self.player = InventoryPlayer()
		self.window = None

	def hold_item(self, wanted_id, wanted_meta=-1):
		""" Returns True if a stack of the specified item ID
		could be placed in the hotbar and selected,
		False otherwise. """

		def wanted(slot):  # check if the slot contains the wanted stack
			slot_id, slot_meta = slot.item_id, slot.damage
			return wanted_id == slot_id and wanted_meta in (-1, slot_meta)

		slot = self.player.hotbar_slots()[self.selected_slot]
		if wanted(slot): return True # already selected
		# not selected, search for it
		# hotbar is at the end of the inventory, search there first
		for slot_nr, slot in enumerate(self.player.hotbar_slots()):
			if wanted(slot):
				self.select_slot(slot_nr)
				return True
		# not in hotbar, search inventory
		for slot_nr, slot in enumerate(self.player.slots):
			if wanted(slot):
				self.swap_into_hotbar(slot_nr)
				return True
		# not in inventory, search open window
		for slot_nr, slot in enumerate(self.window.slots):
			if wanted(slot):
				self.swap_into_hotbar(slot_nr, player_inv=False)
				return True
		return False

	def select_slot(self, slot_nr):
		if 0 <= slot_nr < 9:
			self.selected_slot = slot_nr
			self.net.push_packet('PLAY>Held Item Change', {'slot': slot_nr})

	def shift_click(self, slot, player_inv=True):
		self.click_window(slot, INV_BUTTON_LEFT, INV_MODE_SHIFT, player_inv)

	def swap_into_hotbar(self, slot, hotbar_slot=None, player_inv=True):
		if hotbar_slot is None: hotbar_slot = self.selected_slot
		self.click_window(slot, hotbar_slot, INV_MODE_SWAP_HOTBAR, player_inv)

	def swap_slots(self, slot_a, slot_b, player_inv=True):
		# swap A into hotbar
		self.swap_into_hotbar(slot_a, 0, player_inv)
		# swap A with B, B then is in hotbar
		self.swap_into_hotbar(slot_b, 0, player_inv)
		# swap B to A's original position, restore hotbar
		self.swap_into_hotbar(slot_a, 0, player_inv)

	def click_window(self, slot, button, mode, player_inv=True):
		window = self.player if player_inv else self.window
		# make sure slot is in inventory,
		# allows for slot = -9 as first slot of hotbar etc.
		slot_count = len(window.slots)
		slot += slot_count
		slot %= slot_count
		# action ID gets added in _send_click
		self._send_click({
			'window_id': window.window_id,
			'slot': slot,
			'button': button,
			'mode': mode,
			'clicked_item': {'id': -1},
		})

@pl_announce('Inventory')
class InventoryPlugin:
	def __init__(self, ploader, settings):
		self.clinfo = ploader.requires('ClientInfo')
		self.event = ploader.requires('Event')
		self.net = ploader.requires('Net')
		self.inventory = InventoryCore(self.net, self.send_click)
		ploader.provides('Inventory', self.inventory)

		# Inventory events
		ploader.reg_event_handler(
			'PLAY<Held Item Change', self.handle_held_item_change)
		ploader.reg_event_handler(
			'PLAY<Open Window', self.handle_open_window)
		ploader.reg_event_handler(
			'PLAY<Close Window', self.handle_close_window)
		ploader.reg_event_handler(
			'PLAY<Set Slot', self.handle_set_slot)
		ploader.reg_event_handler(
			'PLAY<Window Items', self.handle_window_items)
		ploader.reg_event_handler(
			'PLAY<Window Property', self.handle_window_prop)
		ploader.reg_event_handler(
			'PLAY<Confirm Transaction', self.handle_confirm_transact)

		# click sending queue
		self.action_id = 0
		self.click_queue = deque()
		self.last_click = None  # stores the last click action for confirmation

	def handle_held_item_change(self, event, packet):
		self.inventory.selected_slot = packet.data['slot']
		self.event.emit('inv_held_item_change', packet.data)

	def handle_open_window(self, event, packet):
		logger.debug('open window %s', packet.data)  # TODO remove
		self.inventory.window = inv_types[packet.data['inv_type']](**packet.data)
		self.event.emit('inv_open_window', {'window': self.inventory.window})

	def handle_close_window(self, event, packet):
		self.event.emit('inv_close_window', {'window': self.inventory.window})
		self.inventory.window = None

	def handle_set_slot(self, event, packet):
		window_id = packet.data['window_id']
		# Notchian server sends window_id = slot_nr = -1 on /clear and login
		if window_id == -1:
			self.event.emit('inv_clear_window', packet.data)
		else:
			self.set_slot_in_window(window_id, packet.data['slot'], **packet.data['slot_data'])

	def handle_window_items(self, event, packet):
		for slot_nr, slot_data in enumerate(packet.data['slots']):
			self.set_slot_in_window(packet.data['window_id'], slot_nr, **slot_data)

	def handle_window_prop(self, event, packet):
		self.get_window_from_id(packet.data['window_id']).properties[packet.data['property']] = packet.data['value']
		self.event.emit('inv_win_prop', packet.data)

	def handle_confirm_transact(self, event, packet):
		if not packet.data['accepted']:
			# try again TODO never occured during testing, check if this works
			self.last_click['action'] = self.get_next_action_id()
			logger.warn('Click not accepted, trying again: %s', self.last_click)
			self.net.push_packet('PLAY>Click Window', self.last_click)
			self.event.emit('inv_click_not_accepted', self.last_click)
			return
		# TODO check if the wrong action ID was confirmed, never occured during testing
		self.update_slots(self.last_click)
		self.last_click = None
		self.try_send_next_packet()
		self.event.emit('inv_click_accepted', packet.data)

	def send_click(self, click):
		# put packet into queue to wait for confirmation
		self.click_queue.append(click)
		self.try_send_next_packet()

	def try_send_next_packet(self):
		# only send if all previous packets got confirmed
		if self.last_click is None and len(self.click_queue) > 0:
			self.last_click = packet = self.click_queue.popleft()
			packet['action'] = self.get_next_action_id()
			self.net.push_packet('PLAY>Click Window', packet)

	def get_next_action_id(self):
		self.action_id += 1
		return self.action_id

	def get_window_from_id(self, window_id):
		return self.inventory.player if window_id == INV_WINID_PLAYER else self.inventory.window

	def set_slot_in_window(self, window_id, slot_nr, **slot_data):
		window = self.get_window_from_id(window_id)
		window.slots[slot_nr] = Slot(**slot_data)
		data = {
			'window': window,
			'slot_nr': slot_nr,
		}.update(slot_data)
		self.event.emit('inv_set_slot', data)

	def update_slots(self, click):
		pass  # FIXME IMPORTANT change the slots in main inventory accordingly
