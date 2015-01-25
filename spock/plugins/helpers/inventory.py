"""
Inventory plugin is a helper plugin for dealing with interaction with inventories
"""

from collections import deque
from spock.utils import pl_announce
from spock.mcp import mcdata, mcpacket

class InventoryCore:
	def __init__(self, clinfo, net):
		self.clinfo = clinfo
		self.net = net
		self.action = 0
		self.clickque = deque()
	
	def click_window(slot, button, mode):
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
		self.inventory = InventoryCore(self.clinfo, self.net)
		ploader.provides('Inventory', self.inventory)
		ploader.reg_event_handler('event_tick', self.tick)

	def tick(self, event, data):
		pass


