"""
Asynchronous task wrappers for inventory
"""
from spockbot.mcdata import constants
from spockbot.plugins.tools.task import TaskFailed, check_key


def unpack_slots_list(slots):
    if len(slots) > 1 or isinstance(slots[0], int) \
            or hasattr(slots[0], 'slot_nr'):
        return slots
    return slots[0]


class InventoryAsync(object):
    def __init__(self, inventory):
        self.inventory = inventory

    def click_slot(self, slot, right=False):
        if isinstance(slot, int):
            slot = self.inventory.window.slots[slot]
        old_slot = slot.copy()
        old_cursor = self.inventory.cursor_slot.copy()

        action_id = self.inventory.click_slot(slot, right)
        if not action_id:
            raise TaskFailed('Click slot failed: not clicked')
        yield 'inventory_click_response', check_key('action_id', action_id)
        # TODO make sure window is not closed while clicking

        empty_cursor = old_cursor.is_empty
        if old_slot.amount == old_slot.item.stack_size and not empty_cursor \
                or old_slot.is_empty and empty_cursor:
            return  # no need to check

        new_slot = self.inventory.window.slots[old_slot.slot_nr]
        new_cursor = self.inventory.cursor_slot
        if new_slot.matches(old_slot) and new_cursor.matches(old_cursor):
            raise TaskFailed('Click slot failed: slot %i did not change (%s)'
                             % (old_slot.slot_nr, old_slot))

    def drop_slot(self, slot=None, drop_stack=False):
        old_index = getattr(slot, 'slot_nr', slot)

        action_id = self.inventory.drop_slot(slot, drop_stack)
        if not action_id:
            raise TaskFailed('Drop slot failed: not clicked')
        yield 'inventory_click_response', check_key('action_id', action_id)

        new_slot = self.inventory.window.slots[old_index]
        if drop_stack and old_index is not None and new_slot.amount > 0:
            raise TaskFailed('Drop slot failed: slot %i not empty' % old_index)

    def creative_set_slot(self, slot_nr=None, slot_dict=None, slot=None):
        self.inventory.creative_set_slot(slot_nr, slot_dict, slot)
        slot_nr = slot_nr if slot is None else slot.slot_nr
        e, data = yield ('inventory_set_slot',
                         lambda e, data: data['slot'].slot_nr == slot_nr)
        if False:  # TODO implement check, for now just assume it worked
            raise TaskFailed('Creative set slot failed: not set')

    def store_or_drop(self):
        """
        Stores the cursor item or drops it if the inventory is full.
        Tip: look directly up or down before calling this, so you can
        pick up the dropped item when the inventory frees up again.

        Returns:
            Slot: The slot used to store it, or None if dropped.
        """
        inv = self.inventory
        if inv.cursor_slot.is_empty:  # nothing to drop
            raise StopIteration(None)

        storage = inv.inv_slots_preferred
        if inv.window.is_storage:
            storage += inv.window.window_slots
        first_empty_slot = inv.find_slot(constants.INV_ITEMID_EMPTY, storage)
        if first_empty_slot is not None:
            yield self.click_slot(first_empty_slot)
        else:
            yield self.drop_slot(drop_stack=True)

        if not inv.cursor_slot.is_empty:
            raise TaskFailed('Store or Drop failed: cursor is not empty')

        raise StopIteration(first_empty_slot)

    def click_slots(self, *slots):
        slots = unpack_slots_list(slots)
        for i, slot in enumerate(slots):
            try:
                yield self.click_slot(slot)
            except TaskFailed as e:
                raise TaskFailed('Clicking %i failed (step %i/%i): %s'
                                 % (slot, i + 1, len(slots), e.args))

    def swap_slots(self, a, b):
        def slot(i):
            return self.inventory.window.slots[i]

        a = getattr(a, 'slot_nr', a)
        b = getattr(b, 'slot_nr', b)
        a_old, b_old = slot(a).copy(), slot(b).copy()

        if not slot(a).is_empty or not self.inventory.cursor_slot.is_empty:
            yield self.click_slot(a)

        if not slot(b).is_empty or not self.inventory.cursor_slot.is_empty:
            yield self.click_slot(b)

        if not slot(a).is_empty or not self.inventory.cursor_slot.is_empty:
            yield self.click_slot(a)

        if not slot(a).matches(b_old) or not slot(b).matches(a_old):
            raise TaskFailed('Failed to swap slots %i and %i' % (a, b))

    def transfer_slots(self, source_slots, target_slots):
        for slot in source_slots:
            if slot.is_empty:
                continue
            item_id_empty = constants.INV_ITEMID_EMPTY
            target = self.inventory.find_slot(item_id_empty, target_slots)
            if target is None:
                raise TaskFailed('Transfer slots failed: target slots full')
            yield self.swap_slots(slot, target)

    def move_to_inventory(self, *slots):
        slots = unpack_slots_list(slots)
        return self.transfer_slots(slots, self.inventory.inv_slots_preferred)

    def move_to_window(self, *slots):
        slots = unpack_slots_list(slots)
        return self.transfer_slots(slots, self.inventory.window.window_slots)

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
