"""
The Inventory plugin keeps track of open windows and their slots.
It offers convenient methods to interact with open windows.
"""

from collections import deque
from spock.utils import pl_announce

# the button codes used in send_click
INV_BUTTON_LEFT = 0
INV_BUTTON_RIGHT = 1
INV_BUTTON_MIDDLE = 2
INV_BUTTON_DROP_SINGLE = 0
INV_BUTTON_DROP_STACK = 1
INV_BUTTON_DRAG_LEFT_START = 0
INV_BUTTON_DRAG_LEFT_ADD = 1
INV_BUTTON_DRAG_LEFT_END = 2
INV_BUTTON_DRAG_RIGHT_START = 4
INV_BUTTON_DRAG_RIGHT_ADD = 5
INV_BUTTON_DRAG_RIGHT_END = 6

# the modes used in send_click
INV_MODE_CLICK = 0
INV_MODE_SHIFT = 1
INV_MODE_SWAP_HOTBAR = 2
INV_MODE_MIDDLE = 3
INV_MODE_DROP = 4
INV_MODE_PAINT = 5
INV_MODE_DOUBLECLICK = 6

# player inventory window ID/type, not opened but updated by server
INV_WINID_PLAYER = 0
INV_TYPE_PLAYER = -1  # non-official, used internally to avoid ID collisions

INV_ITEMID_EMPTY = -1

INV_SLOTS_PLAYER = 9  # crafting and armor
INV_SLOTS_INVENTORY = 9 * 3  # above hotbar
INV_SLOTS_HOTBAR = 9
INV_SLOTS_ADD = INV_SLOTS_INVENTORY + INV_SLOTS_HOTBAR  # always accessible

class Slot:
	def __init__(self, id=INV_ITEMID_EMPTY, amount=0, damage=0, nbt=None):
		self.item_id = id
		self.amount = amount
		self.damage = damage
		# dict of ench_id -> ench_level
		self.nbt = nbt

	def stacks_with(self, other):
		if self.item_id != other.item_id: return False
		if self.damage != other.damage: return False
		if self.damage != other.damage: return False
		raise NotImplementedError('Stacks might differ by NBT data')
		# if self.nbt != other.nbt: return False  # TODO implement this correctly
		# return True

	def max_amount(self):
		# TODO add the real values for ALL THE ITEMS!
		raise NotImplementedError()

	def get_packet_data(self):
		""" Formats the slot for network packing.
		Usually not needed because of the server-side inventory,
		sending {'id': INV_ITEMID_EMPTY} is sufficient. """
		return {'id': INV_ITEMID_EMPTY}
		# TODO implement NBT packing properly
		# data = {'id': self.item_id, 'amount': self.amount, 'damage': self.damage}
		# if self.enchants is not None:
		# 	data['enchants'] = self.enchants
		# return data

	def __str__(self):
		if self.item_id == INV_ITEMID_EMPTY: return 'Empty Slot'
		return 'Slot(%s)' % self.get_packet_data()

# look up a class by window type ID when opening windows
inv_types = {}
def map_window_type(inv_type_id):
	def inner(cl):
		inv_types[inv_type_id] = cl
		cl.inv_type = inv_type_id
		return cl
	return inner

class InventoryBase:
	""" Base class for all inventory types. """

	# the arguments must have the same names as the keys in the packet dict
	def __init__(self, inv_type, window_id, title, slot_count, add_slots):
		self.inv_type = inv_type
		self.window_id = window_id
		self.title = title

		# slots vary by inventory type, but always contain main inventory and hotbar
		self.slots = ([Slot()] * slot_count) + add_slots[-INV_SLOTS_ADD:]

		# additional info dependent on inventory type, dynamically updated by server
		self.properties = {}

	def inventory_index(self):
		return len(self.slots) - INV_SLOTS_ADD

	def hotbar_index(self):
		return len(self.slots) - INV_SLOTS_HOTBAR

	def inventory_slots(self):
		return self.slots[-INV_SLOTS_ADD:-INV_SLOTS_HOTBAR]

	def hotbar_slots(self):
		return self.slots[-INV_SLOTS_HOTBAR:]

	def window_slots(self):
		""" All slots except inventory and hotbar.
		 Useful for searching. """
		return self.slots[:-INV_SLOTS_ADD]

# no @map_window_type(), because not opened by server
class InventoryPlayer(InventoryBase):
	""" The player's inventory is always open when no other window is open. """

	name = 'Inventory'

	def __init__(self, add_slots=[Slot()] * INV_SLOTS_ADD):
		super().__init__(-1, INV_WINID_PLAYER, self.name, INV_SLOTS_PLAYER, add_slots)  # TODO title should be in chat format

	def craft_result_slot(self):
		return self.slots[0]

	def craft_grid_slots(self):
		return self.slots[1:5]

	def armor_slots(self):
		return self.slots[5:9]

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

	# TODO crafting recipes? might be done in other plugin, as this is very complex

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

	# TODO enchanting

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
	# TODO trading

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

	# TODO choosing/applying the effect

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
	""" Handles operations with and contains the player inventory. """

	def __init__(self, net, queue_click):
		self._net = net
		self._queue_click = queue_click  # method to queue a click action, used in click_window
		self.selected_slot = 0
		self.cursor_slot = Slot()  # the slot that moves with the mouse when clicking a slot
		self.window = InventoryPlayer()  # TODO rename? as other plugins access this quite often

	def hold_item(self, wanted_id, wanted_meta=-1):
		""" Tries to place a stack of the specified item ID
		in the hotbar and select it.
		If successful, returns where it was found
		(string, one of 'hand', 'hotbar', 'inventory', 'window'),
		otherwise '' (empty string). """

		def wanted(slot):  # check if the slot contains the wanted stack
			slot_id, slot_meta = slot.item_id, slot.damage
			return wanted_id == slot_id and wanted_meta in (-1, slot_meta)

		slot = self.window.hotbar_slots()[self.selected_slot]
		if wanted(slot): return 'hand'
		# not selected, search for it
		# hotbar is at the end of the inventory, search there first
		for slot_nr, slot in enumerate(self.window.hotbar_slots()):
			if wanted(slot):
				self.select_slot(slot_nr + self.window.hotbar_index())
				return 'hotbar'
		# not in hotbar, search inventory
		for slot_nr, slot in enumerate(self.window.inventory_slots()):
			if wanted(slot):
				self.swap_with_hotbar(slot_nr + self.window.inventory_index())
				return 'inventory'
		# not in inventory, search open window's slots
		for slot_nr, slot in enumerate(self.window.window_slots()):
			if wanted(slot):
				self.swap_with_hotbar(slot_nr)
				return 'window'
		return ''

	def select_slot(self, slot_nr):
		if 0 <= slot_nr < INV_SLOTS_HOTBAR:
			self.selected_slot = slot_nr
			self._net.push_packet('PLAY>Held Item Change', {'slot': slot_nr})

	def shift_click(self, slot):
		self.click_window(slot, INV_BUTTON_LEFT, INV_MODE_SHIFT)

	def swap_with_hotbar(self, slot, hotbar_slot=None):
		if hotbar_slot is None: hotbar_slot = self.selected_slot
		# TODO not implemented yet (see simulate_click)
		# self.click_window(slot, hotbar_slot, INV_MODE_SWAP_HOTBAR)
		self.swap_slots(slot, hotbar_slot + self.window.hotbar_index())

	def swap_slots(self, slot_a, slot_b):
		# pick up A
		self.click_window(slot_a)
		# pick up B, place A at B's position
		self.click_window(slot_b)
		# place B at A's original position
		self.click_window(slot_a)

	def drop_item(self, slot=None, drop_stack=False):
		if slot is None:  # drop held item
			slot = self.selected_slot + self.window.hotbar_index()
		button = INV_BUTTON_DROP_STACK if drop_stack else INV_BUTTON_DROP_SINGLE
		self.click_window(slot, button, INV_MODE_DROP)

	def click_window(self, slot, button=INV_BUTTON_LEFT, mode=INV_MODE_CLICK):
		# make sure slot is in inventory,
		# allows for slot = -INV_SLOTS_HOTBAR as first slot of hotbar etc.
		slot_count = len(self.window.slots)
		slot += slot_count
		slot %= slot_count
		# action ID gets added in _send_click
		self._queue_click({
			'window_id': self.window.window_id,
			'slot': slot,
			'button': button,
			'mode': mode,
			'clicked_item': self.window.slots[slot].get_packet_data(),
		})

	# TODO is/should this be implemented somewhere else?
	def interact_with_block(self, coords):
		""" Clicks on a block to open its window.
		`coords` is a Vec3 with the block coordinates. """
		packet = {
			'location': coords.get_dict(),
			'direction': 1,
			'held_item': self.get_held_item().get_packet_data(),
			'cur_pos_x': 8,
			'cur_pos_y': 8,
			'cur_pos_z': 8,
		}
		self._net.push_packet('PLAY>Player Block Placement', packet)

	def close_window(self):
		self._net.push_packet('PLAY>Close Window', {'window_id': self.window.window_id})

	def get_held_item(self):
		return self.window.slots[self.selected_slot + self.window.hotbar_index()]

@pl_announce('Inventory')
class InventoryPlugin:
	def __init__(self, ploader, settings):
		self.clinfo = ploader.requires('ClientInfo')
		self.event = ploader.requires('Event')
		self.net = ploader.requires('Net')
		self.inventory = InventoryCore(self.net, self.queue_click)
		ploader.provides('Inventory', self.inventory)

		# Inventory events
		ploader.reg_event_handler(
			'PLAY<Held Item Change', self.handle_held_item_change)
		ploader.reg_event_handler(
			'PLAY<Set Slot', self.handle_set_slot)
		ploader.reg_event_handler(
			'PLAY<Window Items', self.handle_window_items)
		ploader.reg_event_handler(
			'PLAY<Window Property', self.handle_window_prop)
		ploader.reg_event_handler(
			'PLAY<Confirm Transaction', self.handle_confirm_transact)
		ploader.reg_event_handler(
			'PLAY<Open Window', self.handle_open_window)
		ploader.reg_event_handler(
			'PLAY<Close Window', self.handle_close_window)
		# also register to serverbound, as server does not send Close Window when we do
		ploader.reg_event_handler(
			'PLAY>Close Window', self.handle_close_window)

		# click sending queue
		self.click_queue = deque()
		self.action_id = 0
		self.last_click = None  # stores the last click action for confirmation

	def handle_held_item_change(self, event, packet):
		self.inventory.selected_slot = packet.data['slot']
		self.event.emit('inv_held_item_change', packet.data)

	def handle_open_window(self, event, packet):
		old_queue = list(self.click_queue)
		self.click_queue.clear() # TODO only remove clicks that affect the previously opened window (player inv)?
		InvNew = inv_types[packet.data['inv_type']]
		self.inventory.window = InvNew(add_slots=self.inventory.window.slots, **packet.data)
		self.event.emit('inv_click_queue_cleared', {'reason': 'open_window', 'actions': old_queue})
		self.event.emit('inv_open_window', {'window': self.inventory.window})

	def handle_close_window(self, event, packet):
		old_queue = list(self.click_queue)
		self.click_queue.clear() # TODO only remove clicks that affect the closed window?
		closed_window = self.inventory.window
		self.inventory.window = InventoryPlayer(add_slots=closed_window.slots)
		self.event.emit('inv_click_queue_cleared', {'reason': 'close_window', 'actions': old_queue})
		self.event.emit('inv_close_window', {'window': closed_window})

	def handle_set_slot(self, event, packet):
		window_id = packet.data['window_id']
		# Notchian server sends window_id = slot_nr = INV_SLOT_EMPTY on /clear and window_close
		if window_id == INV_ITEMID_EMPTY:
			self.event.emit('inv_clear_window', packet.data)
		else:
			self.set_slot(packet.data['slot'], **packet.data['slot_data'])

	def handle_window_items(self, event, packet):
		for slot_nr, slot_data in enumerate(packet.data['slots']):
			self.set_slot(slot_nr, **slot_data)

	def set_slot(self, slot_nr, **slot_data):
		self.inventory.window.slots[slot_nr] = Slot(**slot_data)
		# re-use slot_data for event emission
		slot_data['slot_nr'] = slot_nr
		self.event.emit('inv_set_slot', slot_data)

	def handle_window_prop(self, event, packet):
		self.inventory.window.properties[packet.data['property']] = packet.data['value']
		self.event.emit('inv_win_prop', packet.data)

	def handle_confirm_transact(self, event, packet):
		if not packet.data['accepted']:
			# try again TODO never occured during testing, check if this works
			self.last_click['action'] = self.get_next_action_id()
			self.net.push_packet('PLAY>Click Window', self.last_click)
			self.event.emit('inv_click_not_accepted', self.last_click)
			return
		# TODO check if the wrong action ID was confirmed, never occured during testing
		self.simulate_click(self.last_click)
		last_click, self.last_click = self.last_click, None
		self.try_send_next_packet()
		self.event.emit('inv_click_accepted', last_click)

	def queue_click(self, click):
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

	def simulate_click(self, click_action):
		""" Changes the slots in main inventory according to a click action,
		because the server does not send slot updates after successful clicks. """
		slot_nr, button, mode = click_action['slot'], click_action['button'], click_action['mode']
		inv = self.inventory
		slots = inv.window.slots
		clicked_slot = slots[slot_nr]
		if mode == INV_MODE_CLICK:
			def swap_click():
				inv.cursor_slot, slots[slot_nr] = slots[slot_nr], inv.cursor_slot
			if button == INV_BUTTON_LEFT:
				if clicked_slot.stacks_with(inv.cursor_slot):
					space_left_in_clicked_slot = clicked_slot.max_amount() - clicked_slot.amount
					if space_left_in_clicked_slot > 0:
						put_amount = min(space_left_in_clicked_slot, inv.cursor_slot.amount)
						clicked_slot.amount += put_amount
						inv.cursor_slot.amount -= put_amount
					# else: clicked slot is full, do nothing
				else:
					swap_click()
			elif button == INV_BUTTON_RIGHT:
				if inv.cursor_slot.item_id == INV_ITEMID_EMPTY:
					# take half, round up
					take_amount = (clicked_slot.amount + 1) // 2
					inv.cursor_slot = Slot(clicked_slot.item_id, take_amount, clicked_slot.damage, clicked_slot.nbt)
					clicked_slot.amount -= take_amount
				else:  # already holding an item
					if clicked_slot.stacks_with(inv.cursor_slot):
						# try to transfer one item
						if clicked_slot.amount < clicked_slot.max_amount():
							clicked_slot.amount += 1
							inv.cursor_slot.amount -= 1
						# else: clicked slot is full, do nothing
					else:  # slot items do not stack
						if clicked_slot.item_id == INV_ITEMID_EMPTY:
							if inv.cursor_slot.amount > 1:
								inv.cursor_slot.amount -= 1
							else:
								inv.cursor_slot = Slot()
						else:
							swap_click()
			else: # TODO implement all buttons
				raise NotImplementedError('Clicking with button %i not implemented' % button)
		elif mode == INV_MODE_DROP:
			drop_stack = (INV_BUTTON_DROP_STACK == button)
			if drop_stack:
				clicked_slot.amount = 0
			else:
				clicked_slot.amount -= 1
		else: # TODO implement all click modes
			raise NotImplementedError('Click mode %i not implemented' % mode)
		# clean up empty slots
		if inv.cursor_slot.amount <= 0:
			inv.cursor_slot = Slot()
		if clicked_slot.amount <= 0:
			slots[slot_nr] = Slot()
