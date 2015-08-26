import sys

from minecraft_data.v1_8 import windows as windows_data

from spock.mcdata import constants


class Slot(object):
    def __init__(self, window, slot_nr, id=constants.INV_ITEMID_EMPTY,
                 damage=0, amount=0, enchants=None):
        self.window = window
        self.slot_nr = slot_nr
        self.item_id = id
        self.damage = damage
        self.amount = amount
        self.nbt = enchants

    def move_to_window(self, window, slot_nr):
        self.window, self.slot_nr = window, slot_nr

    def stacks_with(self, other):
        if self.item_id != other.item_id:
            return False
        if self.damage != other.damage:
            return False
        # raise NotImplementedError('Stacks might differ by NBT data: %s %s'
        #                           % (self, other))
        # if self.nbt != other.nbt: return False
        # TODO implement stacking correctly (NBT data comparison)
        return self.max_amount != 1

    @property
    def max_amount(self):
        # TODO use spock.mcdata.items
        # at least use some dummy values for now, ignore 16-stacking items
        items_single = [-1, 256, 257, 258, 259, 261, 282, 326, 327, 333, 335,
                        342, 343, 346, 347, 355, 358, 359, 373, 374, 379, 380,
                        386, 387, 398, 403, 407, 408, 422, 417, 418, 419]
        items_single.extend(range(267, 280))
        items_single.extend(range(283, 287))
        items_single.extend(range(290, 295))
        items_single.extend(range(298, 318))
        items_single.extend(range(2256, 2268))
        for self.item_id in items_single:
            return 1
        return 64

    def get_dict(self):
        """ Formats the slot for network packing. """
        data = {'id': self.item_id}
        if self.item_id != constants.INV_ITEMID_EMPTY:
            data['damage'] = self.damage
            data['amount'] = self.amount
            if self.nbt is not None:
                data['enchants'] = self.nbt
        return data

    def is_empty(self):
        return self.amount <= 0

    def __bool__(self):
        return not self.is_empty()

    def __repr__(self):
        if self.item_id == constants.INV_ITEMID_EMPTY:
            args = 'empty'
        else:  # dirty, but good enough for debugging
            args = str(self.get_dict()) \
                .strip('{}') \
                .replace("'", '') \
                .replace(': ', '=')
        return 'Slot(window=%s, slot_nr=%i, %s)' % (
            self.window, self.slot_nr, args)


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
        :param inv_plugin: inventory plugin instance
        """
        raise NotImplementedError()

    def apply(self, inv_plugin):
        """
        Called by on_success().
        Abstract method.
        :param inv_plugin: inventory plugin instance
        """
        raise NotImplementedError()

    def on_success(self, inv_plugin, emit_set_slot):
        """
        Called when the click was successful
        and should be applied to the inventory.
        :param inv_plugin: inventory plugin instance
        :param emit_set_slot: function to signal a slot change,
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
                              to_slot.max_amount - to_slot.amount)
        if transfer_amount <= 0:
            return
        self.copy_slot_type(from_slot, to_slot)
        to_slot.amount += transfer_amount
        from_slot.amount -= transfer_amount
        self.cleanup_if_empty(from_slot)

    def cleanup_if_empty(self, slot):
        if slot.is_empty():
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
        return {
            'slot': self.slot.slot_nr,
            'button': self.button,
            'mode': 0,
            'clicked_item': self.slot.get_dict(),
        }

    def apply(self, inv_plugin):
        clicked = self.slot
        cursor = inv_plugin.cursor_slot
        if self.button == constants.INV_BUTTON_LEFT:
            if clicked.stacks_with(cursor):
                self.transfer(cursor, clicked, cursor.amount)
            else:
                self.swap_slots(cursor, clicked)
        elif self.button == constants.INV_BUTTON_RIGHT:
            if cursor.item_id == constants.INV_ITEMID_EMPTY:
                # transfer half, round up
                self.transfer(clicked, cursor, (clicked.amount + 1) // 2)
            elif clicked.is_empty() or clicked.stacks_with(cursor):
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
        if inv_plugin.cursor_slot.item_id != constants.INV_ITEMID_EMPTY:
            return None  # can't drop while holding an item
        return {
            'slot': self.slot.slot_nr,
            'button': 1 if self.drop_stack else 0,
            'mode': 4,
            'clicked_item': inv_plugin.cursor_slot.get_dict(),
        }

    def apply(self, inv_plugin):
        if inv_plugin.cursor_slot.is_empty():
            if self.drop_stack:
                self.slot.amount = 0
            else:
                self.slot.amount -= 1
            self.cleanup_if_empty(self.slot)
        # else: cursor not empty, can't drop while holding an item


class InventoryBase(object):
    """ Base class for all inventory types. """

    # the arguments must have the same names as the keys in the packet dict
    def __init__(self, inv_type, window_id, title, slot_count,
                 persistent_slots):
        self.inv_type = inv_type
        self.window_id = window_id
        self.title = title

        # slots vary by inventory type, but always contain main inventory and
        # hotbar create own slots, ...
        self.slots = [Slot(self, slot_nr) for slot_nr in range(slot_count)]
        # ... append persistent slots
        if persistent_slots is None:
            for slot_nr in range(constants.INV_SLOTS_PERSISTENT):
                self.slots.append(Slot(self, slot_nr))
        else:  # persistent slots have to be moved from other inventory
            moved_slots = persistent_slots[-constants.INV_SLOTS_PERSISTENT:]
            for slot_nr, moved_slot in enumerate(moved_slots):
                moved_slot.move_to_window(self, slot_nr + slot_count)
                self.slots.append(moved_slot)

        # additional info dependent on inventory type, dynamically updated
        # by server
        self.properties = {}

    def __repr__(self):
        return 'Inventory(id=%i, title=%s)' % (self.window_id, self.title)

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
        """
        All slots except inventory and hotbar.
        Useful for searching.
        """
        return self.slots[:-constants.INV_SLOTS_PERSISTENT]


def make_window(window):
    """
    Creates a new class for that window and registers it at this module.
    """
    upper_camel_case = lambda word: ''.join(map(str.capitalize, word.split()))
    snake_case = lambda word: '_'.join(map(str.lower, word.split()))

    window = window.copy()
    cls_name = 'Inventory%s' % upper_camel_case(window['name'])
    bases = (InventoryBase,)
    attrs = {
        '__module__': sys.modules[__name__],
        'name': window['name'],
        'inv_type': window['id'],
    }

    for slots in window.get('slots', []):
        attr_name = snake_case(slots['name'])
        index = slots['index']
        size = index + slots.get('size', 1)
        if size == 1:
            def slots_method(self):
                return self.slots[index]
            attr_name += '_slot'
        else:
            def slots_method(self):
                return self.slots[index:index + size]
            attr_name += '_slots'
        slots_method.__name__ = attr_name
        attrs[attr_name] = property(slots_method)

    for i, prop_name in enumerate(window.get('properties', [])):
        def prop_method(self):
            return self.properties[i]
        prop_name = snake_case(prop_name)
        prop_method.__name__ = prop_name
        attrs[prop_name] = property(prop_method)

    for i, button_name in enumerate(window.get('buttons', [])):
        def button_method(self):
            raise NotImplementedError(
                'Button %s is not implemented' % button_name)
        button_name = snake_case(button_name)
        button_method.__name__ = button_name
        attrs[button_name] = button_method  # note: no property method

    cls = type(cls_name, bases, attrs)
    assert not hasattr(sys.modules[__name__], cls_name), \
        'Window "%s" already registered at %s' % (cls_name, __name__)
    setattr(sys.modules[__name__], cls_name, cls)
    return cls


# look up a class by window type ID, e.g. when opening windows
inv_types = {}


def create_windows():
    for window in windows_data:
        cls = make_window(window)
        inv_types[window['id']] = cls


# Create all window classes from minecraft_data
create_windows()
