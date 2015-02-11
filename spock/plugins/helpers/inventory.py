"""
The Inventory plugin keeps track of open windows and their slots.
It offers convenient methods to interact with open windows.

TODO: crafting, getting slots from other windows than main inventory.

Copyright (c) 2015 Gjum.
Licensed under The MIT License, see http://opensource.org/licenses/MIT
"""

__author__ = "Gjum"
__copyright__ = "Copyright (c) 2015 Gjum"
__license__ = "MIT"

from collections import deque
from spock.utils import pl_announce

import logging

logger = logging.getLogger('spock')

# TODO move all this minecraft data stuff elsewhere?

# -1 is the internal entry for the player's inventory.
# It has no official ID, because it is never opened by the server.
# TODO add more slot indices (crafting/trading/enchanting/...)
window_dict = {
	-1: {"id": "minecraft:main", "name": "Inventory",
	     "out_index": 0, "crafting_index": 1, "armor_index": 5, "inventory_index": 9, "hotbar_index": 36},
	 0: {"id": "minecraft:chest", "name": "Chest/Large chest"},
	 1: {"id": "minecraft:crafting_table", "name": "Workbench",
	     "out_index": 0, "crafting_index": 1, "inventory_index": 10, "hotbar_index": 37},
	 2: {"id": "minecraft:furnace", "name": "Furnace",
	     "smelted_index": 0, "fuel_index": 1, "out_index": 2, "inventory_index": 3, "hotbar_index": 30},
	 3: {"id": "minecraft:dispenser", "name": "Dispenser"},
	 4: {"id": "minecraft:enchanting_table", "name": "Enchantment table"},
	 5: {"id": "minecraft:brewing_stand", "name": "Brewing Stand"},
	 6: {"id": "minecraft:villager", "name": "Npc trade"},
	 7: {"id": "minecraft:beacon", "name": "Beacon"},
	 8: {"id": "minecraft:anvil", "name": "Anvil"},
	 9: {"id": "minecraft:hopper", "name": "Hopper"},
	10: {"id": "minecraft:dropper", "name": "Dropper"},
	11: {"id": "EntityHorse", "name": "Horse"},
}

INV_MAIN = -1
INV_CHEST = 0
INV_WORKBENCH = 1
INV_FURNACE = 2
INV_DISPENSER = 3
INV_ECHANTMENT = 4
INV_BREWING = 5
INV_NPC = 6
INV_BEACON = 7
INV_ANVIL = 8
INV_HOPPER = 9
INV_DROPPER = 10
INV_HORSE = 11

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

INV_WINID_MAIN = 0  # main inventory window ID, always open

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

class Window:
	def __init__(self, window_id, inv_type, title, slot_count, eid=None):
		self.window_id = window_id
		self.inv_type = inv_type
		self.title = title
		self.slots = [Slot()] * slot_count
		self.horse_entity_id = eid

	def set_slot(self, slot_nr, **slot_data):
		self.slots[slot_nr] = Slot(**slot_data)

	def get_info(self):
		return window_dict[self.inv_type]

class InventoryCore(dict):
	""" Handles all open windows and their slots.
	Instance is a dict of `Window ID -> Window instance`. """

	def __init__(self, net, send_click):
		super().__init__()  # initialize window dict
		self.net = net
		self._send_click = send_click  # method to queue a click action
		self.selected_slot = 0
		# initialize main inventory, always open, always same ID
		self[INV_WINID_MAIN] = Window(INV_WINID_MAIN, -1, 'Inventory', 45)

	def hold_item(self, wanted_item_id, wanted_item_meta=-1):
		""" Reurns True if a stack of the specified item ID
		could be placed in the hotbar and selected,
		False otherwise. """

		def wanted(slot):  # check if the slot contains the wanted stack
			slot_id, slot_meta = slot.item_id, slot.damage
			return wanted_item_id == slot_id and wanted_item_meta in (-1, slot_meta)

		slot = self.get_hotbar()[self.selected_slot]
		if wanted(slot): return True # already selected
		# not selected, search for it
		# hotbar is at the end of the inventory, search there first
		for slot_nr, slot in enumerate(self.get_hotbar()):
			if wanted(slot):
				self.select_slot(slot_nr)
				return True
		# not in hotbar, search inventory
		# TODO search all slots in all open windows
		for slot_nr, slot in enumerate(self.get_inventory()):
			if wanted(slot):
				self.swap_into_hotbar(slot_nr)
				return True
		return False

	def get_hotbar(self):
		return self[INV_WINID_MAIN].slots[-9:]  # hotbar is always at the end of the window

	def get_inventory(self):
		return self[INV_WINID_MAIN].slots[:-9]  # exclude hotbar

	def select_slot(self, slot_nr):
		if 0 <= slot_nr < 9:
			self.selected_slot = slot_nr
			self.net.push_packet('PLAY>Held Item Change', {'slot': slot_nr})

	def shift_click(self, slot, window_id=None):
		self.click_window(slot, INV_BUTTON_LEFT, INV_MODE_SHIFT, window_id)

	def swap_into_hotbar(self, slot, hotbar_slot=None, window_id=None):
		if hotbar_slot is None: hotbar_slot = self.selected_slot
		self.click_window(slot, hotbar_slot, INV_MODE_SWAP_HOTBAR, window_id)

	def swap_slots(self, slot_a, slot_b, window_id=None):
		""" Swaps the two slots in the specified window. """
		# swap A into hotbar
		self.swap_into_hotbar(slot_a, 0, window_id)
		# swap A with B, B then is in hotbar
		self.swap_into_hotbar(slot_b, 0, window_id)
		# swap B to A's original position, restore hotbar
		self.swap_into_hotbar(slot_a, 0, window_id)

	def click_window(self, slot, button, mode, window_id=None):
		if window_id is None: window_id = self.get_newest_open_window_id()
		# make sure slot is in inventory,
		# allows for slot = -9 as first slot of hotbar etc.
		slot_count = len(self[window_id].slots)
		slot += slot_count
		slot %= slot_count
		# action ID gets added in _send_click
		self._send_click({
			'window_id': window_id,
			'slot': slot,
			'button': button,
			'mode': mode,
			'clicked_item': {'id': -1},
		})

	def get_newest_open_window_id(self):
		return max(self.keys())

@pl_announce('Inventory')
class InventoryPlugin:
	def __init__(self, ploader, settings):
		self.clinfo = ploader.requires('ClientInfo')
		self.event = ploader.requires('Event')
		self.net = ploader.requires('Net')
		self.inventories = InventoryCore(self.net, self.send_click)
		ploader.provides('Inventory', self.inventories)

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
		self.inventories.selected_slot = packet.data['slot']
		self.event.emit('inv_held_item_change', packet.data)

	def handle_open_window(self, event, packet):
		self.inventory[packet.data['window_id']] = Window(**packet.data['window_id'])
		self.event.emit('inv_open_window', packet.data)

	def handle_close_window(self, event, packet):
		if packet.data['window_id'] not in self.inventory:
			logger.error('[Inventory] Could not close %s, ', packet.data['window_id'])
			return
		del self.inventory[packet.data['window_id']]
		self.event.emit('inv_close_window', packet.data)

	def handle_set_slot(self, event, packet):
		window_id = packet.data['window_id']
		# Notchian server sends window_id = slot_nr = -1 on /clear and login
		if window_id != -1:
			self.inventories[window_id].set_slot(packet.data['slot'], **packet.data['slot_data'])
			self.event.emit('inv_set_slot', packet.data)
		else:
			self.event.emit('inv_clear_window', packet.data)

	def handle_window_items(self, event, packet):
		for slot_nr, slot_data in enumerate(packet.data['slots']):
			self.inventories[packet.data['window_id']].set_slot(slot_nr, **slot_data)
			self.event.emit('inv_set_slot', slot_data)

	def handle_window_prop(self, event, packet):
		# TODO packet has 'window_id', 'property', 'value', all numbers, dependent on window type
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

	def update_slots(self, click):
		pass  # FIXME IMPORTANT change the slots in main inventory accordingly
