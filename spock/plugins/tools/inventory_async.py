"""
Asynchronous task wrappers for inventory
"""
from spock.mcdata import constants
from spock.task import TaskFailed


def check_action_id(action_id):
    return lambda event, data: data['action_id'] == action_id


class InventoryAsync(object):
    def __init__(self, inventory):
        self.inventory = inventory

    def click_slot(self, slot, *args, **kwargs):
        if isinstance(slot, int):
            slot = self.inventory.window.slots[slot]
        old_slot = slot.copy()
        old_cursor = self.inventory.cursor_slot.copy()

        action_id = self.inventory.click_slot(slot, *args, **kwargs)
        if not action_id:
            raise TaskFailed('Click slot failed: not clicked')
        yield 'inv_click_response', check_action_id(action_id)
        # TODO make sure window is not closed while clicking

        new_slot = self.inventory.window.slots[old_slot.slot_nr]
        new_cursor = self.inventory.cursor_slot
        if new_slot.matches(old_slot) and new_cursor.matches(old_cursor):
            raise TaskFailed('Click slot failed: slot did not change')

    def drop_slot(self, slot=None, *args, **kwargs):
        # TODO drop_slot is untested
        old_slot = getattr(slot, 'slot_nr', slot)

        action_id = self.inventory.drop_slot(slot, *args, **kwargs)
        if not action_id:
            raise TaskFailed('Drop slot failed: not clicked')
        yield 'inv_click_response', check_action_id(action_id)

        new_slot = self.inventory.window.slots[old_slot]
        if old_slot is not None and new_slot.amount > 0:
            raise TaskFailed('Drop slot failed: not dropped')

    def creative_set_slot(self, slot_nr=None, slot_dict=None, slot=None):
        self.inventory.creative_set_slot(slot_nr, slot_dict, slot)
        slot_nr = slot_nr if slot is None else slot.slot_nr
        e, data = yield ('inv_set_slot',
                         lambda e, data: data['slot'].slot_nr == slot_nr)
        if False:  # TODO implement check, for now just assume it worked
            raise TaskFailed('Creative set slot failed: not set')

    def store_or_drop(self):
        inv = self.inventory
        if inv.window.is_storage:
            storage = inv.inv_slots_preferred + inv.window.window_slots
        else:
            storage = inv.window.persistent_slots
        first_empty_slot = inv.find_slot(constants.INV_ITEMID_EMPTY, storage)
        if first_empty_slot is not None:
            yield self.click_slot(first_empty_slot)
        else:
            yield self.drop_slot(drop_stack=True)

        if inv.cursor_slot.amount > 0:
            raise TaskFailed('Store or Drop failed: cursor is not empty')

    def click_slots(self, *slots):
        if len(slots) == 1 and not isinstance(slots, int) \
                and not hasattr(slots, 'slot_nr'):
            slots = slots[0]  # allow iterable as single argument
        for i, slot in enumerate(slots):
            try:
                yield self.click_slot(slot)
            except TaskFailed as e:
                raise TaskFailed('Clicking %i failed (step %i/%i): %s'
                                 % (slot, i + 1, len(slots), e.args))

    def swap_slots(self, a, b):
        a = getattr(a, 'slot_nr', a)
        b = getattr(b, 'slot_nr', b)
        slot = lambda i: self.inventory.window.slots[i]
        a_old, b_old = slot(a).copy(), slot(b).copy()

        if not slot(a).is_empty or not self.inventory.cursor_slot.is_empty:
            yield self.click_slot(a)

        if not slot(b).is_empty or not self.inventory.cursor_slot.is_empty:
            yield self.click_slot(b)

        if not slot(a).is_empty or not self.inventory.cursor_slot.is_empty:
            yield self.click_slot(a)

        if not slot(a).matches(b_old) or not slot(b).matches(a_old):
            raise TaskFailed('Failed to swap slots %i and %i' % (a, b))

    def move_to_inventory(self, slot):
        target = self.inventory.find_slot(constants.INV_ITEMID_EMPTY,
                                          self.inventory.inv_slots_preferred)
        if target is not None:
            yield self.swap_slots(slot, target)
        else:
            raise TaskFailed('Move to inventory failed: inventory full')

    def move_to_window(self, slot):
        target = self.inventory.find_slot(constants.INV_ITEMID_EMPTY,
                                          self.inventory.window.window_slots)
        if target is not None:
            yield self.swap_slots(slot, target)
        else:
            raise TaskFailed('Move to window failed: window full')

    def hold_item(self, wanted):
        found = self.inventory.find_slot(wanted)
        if not found:
            raise TaskFailed('Could not hold item: not found')
        elif found in self.inventory.window.hotbar_slots:
            self.inventory.select_active_slot(found)
            raise StopIteration('Found item in hotbar')
        else:
            yield self.swap_slots(found, self.inventory.active_slot)
            raise StopIteration('Found item in inventory')
