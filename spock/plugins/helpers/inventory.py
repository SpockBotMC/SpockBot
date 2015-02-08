"""
Inventory plugin is a helper plugin for dealing with interaction with inventories
"""

from collections import deque
from spock.utils import pl_announce
from spock.mcp import mcdata, mcpacket

import logging
logger = logging.getLogger('spock')

INV_MAIN        = "minecraft:main" #not ever sent by the server but a nice way to define player inventory
INV_CHEST       = "minecraft:chest"
INV_WORKBENCH   = "minecraft:crafting_table"
INV_FURNACE     = "minecraft:furnace"
INV_DISPENSER   = "minecraft:dispenser"
INV_ENCHANTMENT = "minecraft:enchanting_table"
INV_BREWING     = "minecraft:brewing_stand"
INV_VILLAGER    = "minecraft:villager"
INV_BEACON      = "minecraft:beacon"
INV_ANVIL       = "minecraft:anvil"
INV_HOPPER      = "minecraft:hopper"
INV_DROPPER     = "minecraft:dropper"
INV_HORSE       = "EntityHorse"

class ExtraInv:
	inv_type = None
	slot_count = 0
	def __init__(self, slots):
		pass

class MainExtraInv(ExtraInv):
	inv_type = INV_MAIN
	slot_count = 9
	def __init__(self, slots):
		self.head = slots[5]
		self.chest = slots[6]
		self.legs = slots[7]
		self.feet = slots[8]
		self.crafting = slots[1:4]
		self.crafting_out = slots[0]

class ChestExtraInv(ExtraInv):
	inv_type = INV_CHEST
	slot_count = 54
	def __init__(self, slots):
		self.slots = slots

class WorkbenchExtraInv(ExtraInv):
	inv_type = INV_WORKBENCH
	slot_count = 10
	def __init__(self, slots):
		self.crafting = slots[1:9]
		self.crafting_out = slots[0]

class FurnaceExtraInv(ExtraInv):
	inv_type = INV_FURNACE
	slot_count = 3
	def __init__(self, slots):
		self.fuel = slots[2]
		self.smelt = slots[1]
		self.output = slots[0]

class DispenserExtraInv(ExtraInv):
	inv_type = INV_DISPENSER
	slot_count = 9
	def __init__(self, slots):
		self.slots = slots

class EnchantmentExtraInv(ExtraInv):
	inv_type = INV_ENCHANTMENT
	slot_count = 0
	def __init__(self, slots):
		self.slots = slots

class BrewingExtraInv(ExtraInv):
	inv_type = INV_BREWING
	slot_count = 0
	def __init__(self, slots):
		self.slots = slots

class VillagerExtraInv(ExtraInv):
	inv_type = INV_VILLAGER
	slot_count = 0
	def __init__(self, slots):
		self.slots = slots

class BeaconExtraInv(ExtraInv):
	inv_type = INV_BEACON
	slot_count = 0
	def __init__(self, slots):
		self.slots = slots

class AnvilExtraInv(ExtraInv):
	inv_type = INV_ANVIL
	slot_count = 0
	def __init__(self, slots):
		self.slots = slots

class HopperExtraInv(ExtraInv):
	inv_type = INV_HOPPER
	slot_count = 0
	def __init__(self, slots):
		self.slots = slots

class DropperExtraInv(ExtraInv):
	inv_type = INV_DROPPER
	slot_count = 0
	def __init__(self, slots):
		self.slots = slots

class HorseExtraInv(ExtraInv):
	inv_type = INV_HORSE
	slot_count = 0
	def __init__(self, slots):
		self.slots = slots

class InventoryCore:
	def __init__(self, net):
		self.net = net
		#window clicky stuff
		self.action = 0
		self.clickque = deque()
		#window storage stuff
		self.window = 0
		self.hotbar = [{'id':-1} for i in range(9)]
		self.main = [{'id':-1} for i in range(27)]
		self.extra = MainExtraInv([{'id':-1} for i in range(9)])

	def click_window(self, slot, button, mode):
		self.clickque.append({
			'window_id': 0,
			'slot': slot,
			'button': button,
			'mode': mode,
			'clicked_item': self.clinfo.inventory.slots[slot],
		})

	def test_inventory(self):
		for i in range(9,43):
			self.action += 1
			data = {
				'window_id': 0,
				'slot': i,
				'button': 0,
				'mode': 0,
				'action': self.action,
				'clicked_item': self.clinfo.inventory.slots[i],
			}
			self.net.push_packet(
				'PLAY>Click Window', data
			)
			self.action += 1
			data = {
				'window_id': 0,
				'slot': i+1,
				'button': 0,
				'mode': 0,
				'action': self.action,
				'clicked_item': self.clinfo.inventory.slots[i+1],
			}
			self.net.push_packet(
				'PLAY>Click Window', data
			)

@pl_announce('Inventory')
class InventoryPlugin:
	def __init__(self, ploader, settings):
		self.clinfo = ploader.requires('ClientInfo')
		self.net = ploader.requires('Net')
		self.inventory = InventoryCore(self.net)
		ploader.provides('Inventory', self.inventory)
		ploader.reg_event_handler('event_tick', self.tick)

		#Inventory Events
		ploader.reg_event_handler(
			'PLAY<Open Window', self.handle_open_window
		)
		ploader.reg_event_handler(
			'PLAY<Close Window', self.handle_close_window
		)
		ploader.reg_event_handler(
			'PLAY<Set Slot', self.handle_set_slot
		)
		ploader.reg_event_handler(
			'PLAY<Window Items', self.handle_window_items
		)
		ploader.reg_event_handler(
			'PLAY<Window Property', self.handle_window_prop
		)
		ploader.reg_event_handler(
			'PLAY<Confirm Transaction', self.handle_confirm_transact
		)

	def tick(self, event, data):
		pass

	def handle_open_window(self, event, packet):
		logger.debug("%s %s", event, packet.data)

	def handle_close_window(self, event, packet):
		logger.debug("%s %s", event, packet.data)

	def handle_set_slot(self, event, packet):
		#logger.debug("%s %s", event, packet.data)
		pass

	def handle_window_items(self, event, packet):
		#logger.debug("%s %s", event, packet.data)
		pass

	def handle_window_prop(self, event, packet):
		logger.debug("%s %s", event, packet.data)

	def handle_confirm_transact(self, event, packet):
		logger.debug("%s %s", event, packet.data)
