import sys
import types

from minecraft_data.v1_8 import windows as windows_by_id
from minecraft_data.v1_8 import windows_list

from spockbot.mcdata import constants, get_item_or_block
from spockbot.mcdata.blocks import Block
from spockbot.mcdata.items import Item
from spockbot.mcdata.utils import camel_case, snake_case


def make_slot_check(wanted):
    """
    Creates and returns a function that takes a slot
    and checks if it matches the wanted item.

    Args:
        wanted: function(Slot) or Slot or itemID or (itemID, metadata)
    """
    if isinstance(wanted, types.FunctionType):
        return wanted  # just forward the slot check function

    if isinstance(wanted, int):
        item, meta = wanted, None
    elif isinstance(wanted, Slot):
        item, meta = wanted.item_id, wanted.damage  # TODO compare NBT
    elif isinstance(wanted, (Item, Block)):
        item, meta = wanted.id, wanted.metadata
    elif isinstance(wanted, str):
        item_or_block = get_item_or_block(wanted, init=True)
        item, meta = item_or_block.id, item_or_block.metadata
    else:  # wanted is (id, meta)
        try:
            item, meta = wanted
        except TypeError:
            raise ValueError('Illegal args for make_slot_check(): %s' % wanted)

    return lambda slot: item == slot.item_id and meta in (None, slot.damage)


class Slot(object):
    def __init__(self, window, slot_nr, id=constants.INV_ITEMID_EMPTY,
                 damage=0, amount=0, enchants=None):
        self.window = window
        self.slot_nr = slot_nr
        self.item_id = id
        self.damage = damage
        self.amount = amount
        self.nbt = enchants
        self.item = get_item_or_block(self.item_id, self.damage) or Item()

    def move_to_window(self, window, slot_nr):
        self.window, self.slot_nr = window, slot_nr

    @property
    def is_empty(self):
        # could also check self.item_id == constants.INV_ITEMID_EMPTY
        return self.amount <= 0

    def matches(self, other):
        return make_slot_check(other)(self)

    def stacks_with(self, other):
        if self.item_id != other.item_id:
            return False
        if self.damage != other.damage:
            return False
        # raise NotImplementedError('Stacks might differ by NBT data: %s %s'
        #                           % (self, other))
        # if self.nbt != other.nbt: return False
        # TODO implement stacking correctly (NBT data comparison)
        return self.item.stack_size != 1

    def get_dict(self):
        """ Formats the slot for network packing. """
        data = {'id': self.item_id}
        if self.item_id != constants.INV_ITEMID_EMPTY:
            data['damage'] = self.damage
            data['amount'] = self.amount
            if self.nbt is not None:
                data['enchants'] = self.nbt
        return data

    def copy(self):
        return Slot(self.window, self.slot_nr, self.item_id,
                    self.damage, self.amount, self.nbt)

    def __bool__(self):
        return not self.is_empty

    def __repr__(self):
        if self.is_empty:
            s = 'empty'
        else:
            item = self.item
            s = '%i/%i %s' % (self.amount, item.stack_size, str(item))

        if self.slot_nr != -1:
            s += ' at %i' % self.slot_nr
        if self.window:
            s += ' in %s' % self.window
        return '<Slot: %s>' % s


class SlotCursor(Slot):
    def __init__(self, id=constants.INV_ITEMID_EMPTY, damage=0, amount=0,
                 enchants=None):
        class CursorWindow(object):  # TODO is there a cleaner way to do this?
            window_id = constants.INV_WINID_CURSOR

            def __repr__(self):
                return 'CursorWindow()'

        super(SlotCursor, self).__init__(
            CursorWindow(), constants.INV_SLOT_NR_CURSOR,
            id, damage, amount, enchants)


class BaseClick(object):
    def get_packet(self, inv_plugin):
        """
        Called by send_click() to prepare the sent packet.
        Abstract method.

        Args:
            inv_plugin (InventoryPlugin): inventory plugin instance
        """
        raise NotImplementedError()

    def apply(self, inv_plugin):
        """
        Called by on_success().
        Abstract method.

        Args:
            inv_plugin (InventoryPlugin): inventory plugin instance
        """
        raise NotImplementedError()

    def on_success(self, inv_plugin, emit_set_slot):
        """
        Called when the click was successful
        and should be applied to the inventory.

        Args:
            inv_plugin (InventoryPlugin): inventory plugin instance
            emit_set_slot (func): function to signal a slot change,
                should be InventoryPlugin().emit_set_slot
        """
        self.dirty = set()
        self.apply(inv_plugin)
        for changed_slot in self.dirty:
            emit_set_slot(changed_slot)

    # helper methods, used by children
    # all argument instances are modified in-place

    def copy_slot_type(self, slot_from, slot_to):
        slot_to.item_id, slot_to.damage = slot_from.item_id, slot_from.damage
        slot_to.nbt = slot_from.nbt
        self.mark_dirty(slot_to)

    def swap_slots(self, slot_a, slot_b):
        slot_a.item_id, slot_b.item_id = slot_b.item_id, slot_a.item_id
        slot_a.damage, slot_b.damage = slot_b.damage, slot_a.damage
        slot_a.amount, slot_b.amount = slot_b.amount, slot_a.amount
        slot_a.nbt, slot_b.nbt = slot_b.nbt, slot_a.nbt
        self.mark_dirty(slot_a)
        self.mark_dirty(slot_b)

    def transfer(self, from_slot, to_slot, max_amount):
        transfer_amount = min(max_amount, from_slot.amount,
                              to_slot.item.stack_size - to_slot.amount)
        if transfer_amount <= 0:
            return
        self.copy_slot_type(from_slot, to_slot)
        to_slot.amount += transfer_amount
        from_slot.amount -= transfer_amount
        self.cleanup_if_empty(from_slot)

    def cleanup_if_empty(self, slot):
        if slot.is_empty:
            empty_slot_at_same_position = Slot(slot.window, slot.slot_nr)
            self.copy_slot_type(empty_slot_at_same_position, slot)
        self.mark_dirty(slot)

    def mark_dirty(self, slot):
        self.dirty.add(slot)


class SingleClick(BaseClick):
    def __init__(self, slot, button=constants.INV_BUTTON_LEFT):
        self.slot = slot
        self.button = button
        if button not in (constants.INV_BUTTON_LEFT,
                          constants.INV_BUTTON_RIGHT):
            raise NotImplementedError(
                'Clicking with button %s not implemented' % button)

    def get_packet(self, inv_plugin):
        slot_nr = self.slot.slot_nr
        if self.slot == inv_plugin.cursor_slot:
            slot_nr = constants.INV_OUTSIDE_WINDOW
        return {
            'slot': slot_nr,
            'button': self.button,
            'mode': 0,
            'clicked_item': self.slot.get_dict(),
        }

    def apply(self, inv_plugin):
        clicked = self.slot
        cursor = inv_plugin.cursor_slot
        if clicked == cursor:
            if self.button == constants.INV_BUTTON_LEFT:
                clicked.amount = 0
            elif self.button == constants.INV_BUTTON_RIGHT:
                clicked.amount -= 1
            self.cleanup_if_empty(clicked)
        elif self.button == constants.INV_BUTTON_LEFT:
            if clicked.stacks_with(cursor):
                self.transfer(cursor, clicked, cursor.amount)
            else:
                self.swap_slots(cursor, clicked)
        elif self.button == constants.INV_BUTTON_RIGHT:
            if cursor.is_empty:
                # transfer half, round up
                self.transfer(clicked, cursor, (clicked.amount + 1) // 2)
            elif clicked.is_empty or clicked.stacks_with(cursor):
                self.transfer(cursor, clicked, 1)
            else:  # slot items do not stack
                self.swap_slots(cursor, clicked)
        else:
            raise NotImplementedError(
                'Clicking with button %s not implemented' % self.button)


class DropClick(BaseClick):
    def __init__(self, slot, drop_stack=False):
        self.slot = slot
        self.drop_stack = drop_stack

    def get_packet(self, inv_plugin):
        if self.slot == inv_plugin.cursor_slot:
            raise ValueError("Can't drop cursor slot, use SingleClick")
        if not inv_plugin.cursor_slot.is_empty:
            raise ValueError("Can't drop other slots: cursor slot is occupied")

        return {
            'slot': self.slot.slot_nr,
            'button': 1 if self.drop_stack else 0,
            'mode': 4,
            'clicked_item': inv_plugin.cursor_slot.get_dict(),
        }

    def apply(self, inv_plugin):
        if self.drop_stack:
            self.slot.amount = 0
        else:
            self.slot.amount -= 1
        self.cleanup_if_empty(self.slot)


class Window(object):
    """ Base class for all inventory types. """

    name = None
    inv_type = None
    inv_data = {}

    # the arguments must have the same names as the keys in the packet dict
    def __init__(self, window_id, title, slot_count,
                 inv_type=None, persistent_slots=None, eid=None):
        assert not inv_type or inv_type == self.inv_type, \
            'inv_type differs: %s instead of %s' % (inv_type, self.inv_type)
        self.is_storage = slot_count > 0  # same after re-opening window
        if not self.is_storage:  # get number of temporary slots
            window_dict = windows_by_id[inv_type]
            if 'slots' in window_dict:
                slot_count = max(slot['index'] + slot.get('size', 1)
                                 for slot in window_dict['slots'])
        self.window_id = window_id
        self.title = title
        self.eid = eid  # used for horses

        # window slots vary, but always end with main inventory and hotbar
        # create own slots, ...
        self.slots = [Slot(self, slot_nr) for slot_nr in range(slot_count)]
        # ... append persistent slots (main inventory and hotbar)
        if persistent_slots is None:
            for slot_nr in range(constants.INV_SLOTS_PERSISTENT):
                self.slots.append(Slot(self, slot_nr + slot_count))
        else:  # persistent slots have to be moved from other inventory
            moved_slots = persistent_slots[-constants.INV_SLOTS_PERSISTENT:]
            for slot_nr, moved_slot in enumerate(moved_slots):
                moved_slot.move_to_window(self, slot_nr + slot_count)
                self.slots.append(moved_slot)

        # additional info dependent on inventory type,
        # dynamically updated by server
        self.properties = {}

    def __repr__(self):
        return '%s(window_id=%i, title=%s, slot_count=%i)' % (
            self.__class__.__name__,
            self.window_id, self.title, len(self.slots))

    @property
    def persistent_slots(self):
        return self.slots[-constants.INV_SLOTS_PERSISTENT:]

    @property
    def inventory_slots(self):
        return self.slots[
            -constants.INV_SLOTS_PERSISTENT:-constants.INV_SLOTS_HOTBAR]

    @property
    def hotbar_slots(self):
        return self.slots[-constants.INV_SLOTS_HOTBAR:]

    @property
    def window_slots(self):
        """All slots except inventory and hotbar. Useful for searching."""
        return self.slots[:-constants.INV_SLOTS_PERSISTENT]


# Helpers for creating the window classes

def _make_window(window_dict):
    """
    Creates a new class for that window and registers it at this module.
    """
    cls_name = '%sWindow' % camel_case(str(window_dict['name']))
    bases = (Window,)
    attrs = {
        '__module__': sys.modules[__name__],
        'name': str(window_dict['name']),
        'inv_type': str(window_dict['id']),
        'inv_data': window_dict,
    }

    # creates function-local index and size variables
    def make_slot_method(index, size=1):
        if size == 1:
            return lambda self: self.slots[index]
        else:
            return lambda self: self.slots[index:(index + size)]

    for slots in window_dict.get('slots', []):
        index = slots['index']
        size = slots.get('size', 1)
        attr_name = snake_case(str(slots['name']))
        attr_name += '_slot' if size == 1 else '_slots'
        slots_method = make_slot_method(index, size)
        slots_method.__name__ = attr_name
        attrs[attr_name] = property(slots_method)

    for i, prop_name in enumerate(window_dict.get('properties', [])):
        def make_prop_method(i):
            return lambda self: self.properties[i]
        prop_method = make_prop_method(i)
        prop_name = snake_case(str(prop_name))
        prop_method.__name__ = prop_name
        attrs[prop_name] = property(prop_method)

    cls = type(cls_name, bases, attrs)
    assert not hasattr(sys.modules[__name__], cls_name), \
        'Window "%s" already registered at %s' % (cls_name, __name__)
    setattr(sys.modules[__name__], cls_name, cls)
    return cls


# look up a class by window type ID, e.g. when opening windows
inv_types = {}


def _create_windows():
    for window in windows_list:
        cls = _make_window(window)
        inv_types[cls.inv_type] = cls

# Create all window classes from minecraft_data
_create_windows()

# get the PlayerWindow, which was just generated during runtime
_player_window = sys.modules[__name__].PlayerWindow


# override constructor of PlayerWindow
def _player_init(self, *args, **kwargs):
    super(_player_window, self).__init__(
        constants.INV_WINID_PLAYER, self.name, constants.INV_SLOTS_PLAYER,
        *args, **kwargs)

setattr(_player_window, '__init__', _player_init)
