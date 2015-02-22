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

INV_WINID_CURSOR = -1  # the slot that follows the cursor
INV_WINID_PLAYER = 0  # player inventory window ID/type, not opened but updated by server
INV_TYPE_PLAYER = -1  # non-official, used internally to avoid ID collisions
INV_ITEMID_EMPTY = -1

INV_SLOTS_PLAYER = 9  # crafting and armor
INV_SLOTS_INVENTORY = 9 * 3  # above hotbar
INV_SLOTS_HOTBAR = 9
INV_SLOTS_ADD = INV_SLOTS_INVENTORY + INV_SLOTS_HOTBAR  # always accessible

class Slot:
	def __init__(self, id=INV_ITEMID_EMPTY, damage=0, amount=0, enchants=None):
		self.item_id = id
		self.damage = damage
		self.amount = amount
		self.nbt = enchants

	def stacks_with(self, other):
		if self.item_id != other.item_id: return False
		if self.damage != other.damage: return False
		if self.damage != other.damage: return False
		if self.item_id == INV_ITEMID_EMPTY: return False  # for now, remove later, workaround for clicking empty slots
		raise NotImplementedError('Stacks might differ by NBT data')
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
		if self.item_id == INV_ITEMID_EMPTY: return 'Slot()'
		args = str(self.get_dict()).strip('{}').replace("'", '').replace(': ', '=')
		return 'Slot(%s)' % args

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
		if hotbar_slot_nr > 0:
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

	def click_slot(self, slot, button=INV_BUTTON_LEFT, mode=INV_MODE_CLICK):
		# make sure slot is in inventory,
		# allows for slot = -INV_SLOTS_HOTBAR as first slot of hotbar etc.
		slot %= len(self.window.slots)
		# action ID gets added in _send_click
		self._queue_click({
			'window_id': self.window.window_id,
			'slot': slot,
			'button': button,
			'mode': mode,
			'clicked_item': self.window.slots[slot].get_dict(),
		})

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
		self.event.emit('inv_click_queue_cleared', {'reason': 'inv_open_window', 'actions': old_queue})
		self.event.emit('inv_open_window', {'window': self.inventory.window})

	def handle_close_window(self, event, packet):
		old_queue = list(self.click_queue)
		self.click_queue.clear() # TODO only remove clicks that affect the closed window?
		closed_window = self.inventory.window
		self.inventory.window = InventoryPlayer(add_slots=closed_window.slots)
		self.event.emit('inv_click_queue_cleared', {'reason': 'inv_close_window', 'actions': old_queue})
		self.event.emit('inv_close_window', {'window': closed_window})

	def handle_set_slot(self, event, packet):
		self.set_slot(**packet)

	def handle_window_items(self, event, packet):
		window_id = packet.data['window_id']
		for slot_nr, slot_data in enumerate(packet.data['slots']):
			self.set_slot(window_id, slot_nr, slot_data)

	def set_slot(self, window_id, slot, slot_data):
		if window_id == INV_WINID_CURSOR and slot == -1:
			self.inventory.cursor_slot = Slot(**slot_data)
		elif window_id == self.inventory.window.window_id:
			self.inventory.window.slots[slot] = Slot(**slot_data)
		else:
			raise ValueError('Unexpected window ID (%i) or slot (%i)' % (window_id, slot))
		self.emit_set_slot(window_id, slot, slot_data)

	def emit_set_slot(self, window_id, slot_nr, slot_data):
		emit_data = {'window_id': window_id, 'slot_nr': slot_nr, 'slot': Slot(**slot_data)}
		self.event.emit('inv_set_slot', emit_data)

	def handle_window_prop(self, event, packet):
		self.inventory.window.properties[packet.data['property']] = packet.data['value']
		self.event.emit('inv_win_prop', packet.data)

	def handle_confirm_transact(self, event, packet):
		if not packet.data['accepted']:
			# try again TODO what should be done here?
			# Server sends all slots again, but seems to stop sending any confirm packets...
			self.last_click['action'] = self.get_next_action_id()
			self.net.push_packet('PLAY>Click Window', self.last_click)
			self.event.emit('inv_click_not_accepted', self.last_click)
			return
		# TODO check if the wrong action ID was confirmed, never occured during testing
		self.simulate_click(self.last_click)
		last_click, self.last_click = self.last_click, None
		self.event.emit('inv_click_accepted', last_click)
		self.try_send_next_packet()

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
		old_cursor_slot = inv.cursor_slot
		old_window_slot = slots[slot_nr]
		if mode == INV_MODE_CLICK:
			def swap_click():
				inv.cursor_slot, slots[slot_nr] = slots[slot_nr], inv.cursor_slot
			if button == INV_BUTTON_LEFT:
				if slots[slot_nr].stacks_with(inv.cursor_slot):
					space_left_in_clicked_slot = slots[slot_nr].max_amount() - slots[slot_nr].amount
					if space_left_in_clicked_slot > 0:
						put_amount = min(space_left_in_clicked_slot, inv.cursor_slot.amount)
						slots[slot_nr].amount += put_amount
						inv.cursor_slot.amount -= put_amount
					# else: clicked slot is full, do nothing
				else:
					swap_click()
			elif button == INV_BUTTON_RIGHT:
				if inv.cursor_slot.item_id == INV_ITEMID_EMPTY:
					# take half, round up
					take_amount = (slots[slot_nr].amount + 1) // 2
					inv.cursor_slot = Slot(slots[slot_nr].item_id, slots[slot_nr].damage, take_amount, slots[slot_nr].nbt)
					slots[slot_nr].amount -= take_amount
				else:  # already holding an item
					if slots[slot_nr].stacks_with(inv.cursor_slot):
						# try to transfer one item
						if slots[slot_nr].amount < slots[slot_nr].max_amount():
							slots[slot_nr].amount += 1
							inv.cursor_slot.amount -= 1
						# else: clicked slot is full, do nothing
					else:  # slot items do not stack
						if slots[slot_nr].item_id == INV_ITEMID_EMPTY:
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
				(slots[slot_nr]).amount = 0
			else:
				slots[slot_nr].amount -= 1
		else: # TODO implement all click modes
			raise NotImplementedError('Click mode %i not implemented' % mode)
		# clean up empty slots
		if inv.cursor_slot.amount <= 0:
			inv.cursor_slot = Slot()
		if slots[slot_nr].amount <= 0:
			slots[slot_nr] = Slot()
		# done updating the slots, now emit set_slot events
		if old_cursor_slot != inv.cursor_slot:
			self.emit_set_slot(INV_WINID_CURSOR, -1, inv.cursor_slot.get_dict())
		if old_window_slot != slots[slot_nr]:
			self.emit_set_slot(self.inventory.window.window_id, slot_nr, slots[slot_nr].get_dict())
