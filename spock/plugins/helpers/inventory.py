"""
The Inventory plugin keeps track of the open window and its slots
and offers convenient methods for inventory manipulation.
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

INV_SLOT_NR_CURSOR = -1
INV_WINID_CURSOR = -1  # the slot that follows the cursor
INV_WINID_PLAYER = 0  # player inventory window ID/type, not opened but updated by server
INV_ITEMID_EMPTY = -1

INV_SLOTS_PLAYER = 9  # crafting and armor
INV_SLOTS_INVENTORY = 9 * 3  # above hotbar
INV_SLOTS_HOTBAR = 9
INV_SLOTS_ADD = INV_SLOTS_INVENTORY + INV_SLOTS_HOTBAR  # always accessible

class Slot:
	def __init__(self, window, slot_nr, id=INV_ITEMID_EMPTY, damage=0, amount=0, enchants=None):
		self.window = window
		self.slot_nr = slot_nr
		self.item_id = id
		self.damage = damage
		self.amount = amount
		self.nbt = enchants

	def move_to_window(self, window, slot_nr):
		self.window, self.slot_nr = window, slot_nr

	def stacks_with(self, other):
		if self.item_id != other.item_id: return False
		if self.damage != other.damage: return False
		if self.damage != other.damage: return False
		if self.item_id == INV_ITEMID_EMPTY: return False  # for now, remove later, workaround for clicking empty slots
		raise NotImplementedError('Stacks might differ by NBT data: %s %s' % (self, other))
		# if self.nbt != other.nbt: return False  # TODO implement this correctly
		# return True

	def max_amount(self):
		# TODO add the real values for ALL THE ITEMS! And blocks.
		raise NotImplementedError()

	def get_dict(self):
		""" Formats the slot for network packing. """
		data = {'id': self.item_id}
		if self.item_id != INV_ITEMID_EMPTY:
			data['damage'] = self.damage
			data['amount'] = self.amount
			if self.nbt is not None:
				data['enchants'] = self.nbt
		return data

	def __repr__(self):
		if self.item_id != INV_ITEMID_EMPTY:
			args = str(self.get_dict()).strip('{}').replace("'", '').replace(': ', '=')
		else: args = 'empty'
		return 'Slot(window=%s, slot_nr=%i, %s)' % (self.window, self.slot_nr, args)

class SlotCursor(Slot):
	def __init__(self, id=INV_ITEMID_EMPTY, damage=0, amount=0, enchants=None):
		class CursorWindow:
			window_id = INV_WINID_CURSOR
			def __repr__(self):
				return 'CursorWindow()'
		super().__init__(CursorWindow(), INV_SLOT_NR_CURSOR, id, damage, amount, enchants)

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
		# create own slots, ...
		self.slots = [Slot(self, slot_nr) for slot_nr in range(slot_count)]
		# ... append player inventory slots, which have to be moved
		for slot_nr_add, inv_slot in enumerate(add_slots[-INV_SLOTS_ADD:]):
			inv_slot.move_to_window(self, slot_nr_add + slot_count)
			self.slots.append(inv_slot)

		# additional info dependent on inventory type, dynamically updated by server
		self.properties = {}

	def __repr__(self):
		return 'Inventory(id=%i, title=%s)' % (self.window_id, self.title)

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

	def __init__(self, add_slots=None):
		if add_slots is None:
			add_slots = [Slot(self, slot_nr) for slot_nr in range(INV_SLOTS_ADD)]
		super().__init__('player', INV_WINID_PLAYER, self.name, INV_SLOTS_PLAYER, add_slots)  # TODO title should be in chat format

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
	""" Handles operations with the player inventory. """

	def __init__(self, net_plugin, click_slot):
		self._net = net_plugin
		self.click_slot = click_slot
		self.selected_slot = 0
		self.cursor_slot = SlotCursor()  # the slot that moves with the mouse when clicking a slot
		self.window = InventoryPlayer()

	def find_item(self, item_id, meta=-1):
		""" Returns the first slot containing the item or False if not found.
		Searches held item, hotbar, player inventory, open window in this order. """

		wanted = lambda s: item_id == s.item_id and meta in (-1, s.damage)

		slot = self.window.hotbar_slots()[self.selected_slot]
		if wanted(slot):
			return self.selected_slot + self.window.hotbar_index()
		# not selected, search for it
		# hotbar is at the end of the inventory, search there first
		for slot_nr, slot in enumerate(self.window.hotbar_slots()):
			if wanted(slot):
				return slot_nr + self.window.hotbar_index()
		# not in hotbar, search inventory
		for slot_nr, slot in enumerate(self.window.inventory_slots()):
			if wanted(slot):
				return slot_nr + self.window.inventory_index()
		# not in inventory, search open window's slots
		for slot_nr, slot in enumerate(self.window.window_slots()):
			if wanted(slot):
				return slot_nr
		return False

	def hold_item(self, item_id, meta=-1):
		""" Tries to place a stack of the specified item ID
		in the hotbar and select it.
		Returns True if successful, False otherwise. """

		slot_nr = self.find_item(item_id, meta)
		if slot_nr is False: return False
		hotbar_slot_nr = slot_nr - self.window.hotbar_index()
		if hotbar_slot_nr >= 0:
			self.select_slot(hotbar_slot_nr)
		else:
			self.swap_with_hotbar(slot_nr)
		return True

	def select_slot(self, slot_nr):
		if 0 <= slot_nr < INV_SLOTS_HOTBAR and slot_nr != self.selected_slot:
			self.selected_slot = slot_nr
			self._net.push_packet('PLAY>Held Item Change', {'slot': slot_nr})

	def shift_click(self, slot):
		# TODO not implemented yet (see simulate_click)
		self.click_slot(slot, INV_BUTTON_LEFT, INV_MODE_SHIFT)

	def swap_with_hotbar(self, slot, hotbar_slot=None):
		if hotbar_slot is None: hotbar_slot = self.selected_slot
		# TODO not implemented yet (see simulate_click)
		# self.click_window(slot, hotbar_slot, INV_MODE_SWAP_HOTBAR)
		self.swap_slots(slot, hotbar_slot + self.window.hotbar_index())

	def swap_slots(self, slot_a, slot_b):
		# pick up A
		self.click_slot(slot_a)
		# pick up B, place A at B's position
		self.click_slot(slot_b)
		# place B at A's original position
		self.click_slot(slot_a)

	def drop_item(self, slot=None, drop_stack=False):
		if slot is None:  # drop held item
			slot = self.selected_slot + self.window.hotbar_index()
		button = INV_BUTTON_DROP_STACK if drop_stack else INV_BUTTON_DROP_SINGLE
		self.click_slot(slot, button, INV_MODE_DROP)

	# TODO is/should this be implemented somewhere else?
	def interact_with_block(self, coords):
		""" Clicks on a block to open its window.
		`coords` is a Vec3 with the block coordinates. """
		packet = {
			'location': coords.get_dict(),
			'direction': 1,
			'held_item': self.get_held_item().get_dict(),
			'cur_pos_x': 8,
			'cur_pos_y': 8,
			'cur_pos_z': 8,
		}
		self._net.push_packet('PLAY>Player Block Placement', packet)

	# TODO is/should this be implemented somewhere else?
	def interact_with_entity(self, entity_id):
		""" Clicks on an entity to open its window. """
		self._net.push_packet('PLAY>Use Entity', {'target': entity_id, 'action': 0})

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
		self.inventory = InventoryCore(self.net, self.click_slot)
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
			'PLAY<Confirm Transaction', self.handle_confirm_transaction)
		ploader.reg_event_handler(
			'PLAY<Open Window', self.handle_open_window)
		ploader.reg_event_handler(
			'PLAY<Close Window', self.handle_close_window)
		# also register to serverbound, as server does not send Close Window when we do
		ploader.reg_event_handler(
			'PLAY>Close Window', self.handle_close_window)

		# click sending
		self.action_id = 0
		self.last_click = None  # stores the last click action for confirmation

	def handle_held_item_change(self, event, packet):
		self.inventory.selected_slot = packet.data['slot']
		self.event.emit('inv_held_item_change', packet.data)

	def handle_open_window(self, event, packet):
		InvNew = inv_types[packet.data['inv_type']]
		self.inventory.window = InvNew(add_slots=self.inventory.window.slots, **packet.data)
		self.event.emit('inv_open_window', {'window': self.inventory.window})

	def handle_close_window(self, event, packet):
		closed_window = self.inventory.window
		self.inventory.window = InventoryPlayer(add_slots=closed_window.slots)
		self.event.emit('inv_close_window', {'window': closed_window})

	def handle_set_slot(self, event, packet):
		self.set_slot(packet.data['window_id'], packet.data['slot'], packet.data['slot_data'])

	def handle_window_items(self, event, packet):
		window_id = packet.data['window_id']
		for slot_nr, slot_data in enumerate(packet.data['slots']):
			self.set_slot(window_id, slot_nr, slot_data)

	def set_slot(self, window_id, slot_nr, slot_data):
		if window_id == INV_WINID_CURSOR and slot_nr == INV_SLOT_NR_CURSOR:
			slot = self.inventory.cursor_slot = SlotCursor(**slot_data)
		elif window_id == self.inventory.window.window_id:
			slot = self.inventory.window.slots[slot_nr] = Slot(self.inventory.window, slot_nr, **slot_data)
		else:
			raise ValueError('Unexpected window ID (%i) or slot_nr (%i)' % (window_id, slot_nr))
		self.emit_set_slot(slot)

	def emit_set_slot(self, slot):
		self.event.emit('inv_set_slot', {'slot': slot})

	def handle_window_prop(self, event, packet):
		self.inventory.window.properties[packet.data['property']] = packet.data['value']
		self.event.emit('inv_win_prop', packet.data)

	def handle_confirm_transaction(self, event, packet):
		last_click, self.last_click = self.last_click, None
		if packet.data['accepted']:
			# TODO check if the wrong window/action ID was confirmed, never occured during testing
			# change the slots in main inventory according to a click action,
			# because the server does not send slot updates after successful clicks
			slot_nr, button, mode = last_click['slot'], last_click['button'], last_click['mode']
			slot = self.inventory.window.slots[slot_nr]
			cursor = self.inventory.cursor_slot
			ClickSimulator(self).simulate(slot, cursor, button, mode)
		else:  # click not accepted
			# confirm that we received this packet
			self.net.push_packet('PLAY>Confirm Transaction', packet.data)
			# server will re-send all slots now

	def click_slot(self, slot, button=INV_BUTTON_LEFT, mode=INV_MODE_CLICK):
		""" Returns True if the click could be sent, False otherwise. """
		# only send if previous packet got confirmed
		if self.last_click is not None:
			return False
		# make sure slot is in inventory,
		# allows for `slot = -INV_SLOTS_HOTBAR` as first slot of hotbar etc.
		slot %= len(self.window.slots)
		# action and clicked_item get added in try_send_next_packet
		packet = {
			'window_id': self.window.window_id,
			'slot': slot,
			'button': button,
			'mode': mode,
		}
		if mode == INV_MODE_DROP:
			if self.cursor_slot.item_id != INV_ITEMID_EMPTY:
				# can't drop while holding an item, skip to next packet
				return False
			packet['clicked_item'] = self.cursor_slot.get_dict()
		else:
			packet['clicked_item'] = self.window.slots[slot].get_dict()
		packet['action'] = self.get_next_action_id()
		# remember packet to wait for confirmation
		self.last_click = packet
		self.net.push_packet('PLAY>Click Window', packet)
		return True

	def get_next_action_id(self):
		self.action_id += 1
		return self.action_id

class ClickSimulator:
	def __init__(self, inv_plugin):
		self.inv_plugin = inv_plugin

	def simulate(self, changed_slot, cursor, button, mode):
		""" Applies the click action to the given slots.
		Returns True if at least one slot changed, False otherwise. """
		self.clicked = changed_slot
		self.cursor = cursor
		self.button = button
		self.mode = mode
		self.dirty = set()  # slots that might have changed, for emit_set_slot
		if self.mode == INV_MODE_CLICK: self.click()
		elif self.mode == INV_MODE_DROP: self.drop()
		else: raise NotImplementedError('Click mode %i not implemented' % self.mode)
		for changed_slot in self.dirty:
			self.inv_plugin.emit_set_slot(changed_slot)

	def click(self):
		if self.button == INV_BUTTON_LEFT: self.left_click()
		elif self.button == INV_BUTTON_RIGHT: self.right_click()
		else: raise NotImplementedError('Clicking with button %i not implemented' % self.button)

	def left_click(self):
		if self.clicked.stacks_with(self.cursor):
			self.transfer(self.cursor, self.clicked, self.cursor.amount)
		else:
			self.swap_slots(self.cursor, self.clicked)

	def right_click(self):
		if self.cursor.item_id == INV_ITEMID_EMPTY:
			# transfer half, round up
			self.transfer(self.clicked, self.cursor, (self.clicked.amount+1) // 2)
		else:  # already holding an item
			if self.clicked.item_id == INV_ITEMID_EMPTY or self.clicked.stacks_with(self.cursor):
				self.transfer(self.cursor, self.clicked, 1)
			else:  # slot items do not stack
				self.swap_slots(self.cursor, self.clicked)

	def drop(self):
		if self.cursor.item_id == INV_ITEMID_EMPTY:
			if self.button == INV_BUTTON_DROP_STACK:
				self.clicked.amount = 0
			else:
				self.clicked.amount -= 1
			self.cleanup_if_empty(self.clicked)
		# else: can't drop while holding an item

	def copy_slot_type(self, slot_from, slot_to):
		slot_to.item_id, slot_to.damage, slot_to.nbt = slot_from.item_id, slot_from.damage, slot_from.nbt
		self.mark_dirty(slot_to)

	def swap_slots(self, slot_a, slot_b):
		slot_a.item_id, slot_b.item_id = slot_b.item_id, slot_a.item_id
		slot_a.damage,  slot_b.damage  = slot_b.damage,  slot_a.damage
		slot_a.amount,  slot_b.amount  = slot_b.amount,  slot_a.amount
		slot_a.nbt,     slot_b.nbt     = slot_b.nbt,     slot_a.nbt
		self.mark_dirty(slot_a)
		self.mark_dirty(slot_b)

	def transfer(self, from_slot, to_slot, max_amount):
		amount = min(max_amount, from_slot.amount, to_slot.max_amount() - to_slot.amount)
		if amount <= 0: return
		self.copy_slot_type(from_slot, to_slot)
		to_slot.amount += amount
		from_slot.amount -= amount
		self.cleanup_if_empty(from_slot)

	def cleanup_if_empty(self, slot):
		if slot.amount <= 0:
			empty_slot_at_same_position = Slot(slot.window, slot.slot_nr)
			self.copy_slot_type(empty_slot_at_same_position, slot)
		self.mark_dirty(slot)

	def mark_dirty(self, slot):
		self.dirty.add(slot)
