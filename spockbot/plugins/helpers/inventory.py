"""
The Inventory plugin keeps track of the inventory
and provides simple inventory analysis and manipulation.
"""
from spockbot.mcdata import constants, windows
from spockbot.mcdata.windows import make_slot_check
from spockbot.plugins.base import PluginBase, pl_announce
from spockbot.plugins.tools.event import EVENT_UNREGISTER
from spockbot.plugins.tools.inventory_async import InventoryAsync


class InventoryCore(object):
    """ Handles operations with the player inventory. """

    def __init__(self, net_plugin, send_click):
        self._net = net_plugin
        self.send_click = send_click
        self.active_slot_nr = 0
        # the slot that moves with the mouse when clicking a slot
        self.cursor_slot = windows.SlotCursor()
        self.window = windows.PlayerWindow()
        self.async = InventoryAsync(self)

    def total_stored(self, wanted, slots=None):
        """
        Calculates the total number of items of that type
        in the current window or given slot range.

        Args:
            wanted: function(Slot) or Slot or itemID or (itemID, metadata)
        """
        if slots is None:
            slots = self.window.slots
        wanted = make_slot_check(wanted)
        return sum(slot.amount for slot in slots if wanted(slot))

    def find_slot(self, wanted, slots=None):
        """
        Searches the given slots or, if not given,
        active hotbar slot, hotbar, inventory, open window in this order.

        Args:
            wanted: function(Slot) or Slot or itemID or (itemID, metadata)

        Returns:
            Optional[Slot]: The first slot containing the item
                            or None if not found.
        """
        for slot in self.find_slots(wanted, slots):
            return slot
        return None

    def find_slots(self, wanted, slots=None):
        """
        Yields all slots containing the item.
        Searches the given slots or, if not given,
        active hotbar slot, hotbar, inventory, open window in this order.

        Args:
            wanted: function(Slot) or Slot or itemID or (itemID, metadata)
        """
        if slots is None:
            slots = self.inv_slots_preferred + self.window.window_slots
        wanted = make_slot_check(wanted)

        for slot in slots:
            if wanted(slot):
                yield slot

    def select_active_slot(self, slot_or_hotbar_index):
        if hasattr(slot_or_hotbar_index, 'slot_nr'):
            hotbar_start = self.window.hotbar_slots[0].slot_nr
            slot_or_hotbar_index = slot_or_hotbar_index.slot_nr - hotbar_start

        assert 0 <= slot_or_hotbar_index < constants.INV_SLOTS_HOTBAR, \
            'Invalid hotbar index %i' % slot_or_hotbar_index

        if self.active_slot_nr != slot_or_hotbar_index:
            self.active_slot_nr = slot_or_hotbar_index
            self._net.push_packet('PLAY>Held Item Change',
                                  {'slot': slot_or_hotbar_index})

    def click_slot(self, slot, right=False):
        """
        Left-click or right-click the slot.

        Args:
            slot (Slot): The clicked slot. Can be ``Slot`` instance or integer.
                         Set to ``inventory.cursor_slot``
                         for clicking outside the window.
        """
        if isinstance(slot, int):
            slot = self.window.slots[slot]
        button = constants.INV_BUTTON_RIGHT \
            if right else constants.INV_BUTTON_LEFT
        return self.send_click(windows.SingleClick(slot, button))

    def drop_slot(self, slot=None, drop_stack=False):
        """
        Drop one or all items of the slot.

        Does not wait for confirmation from the server. If you want that,
        use a ``Task`` and ``yield inventory.async.drop_slot()`` instead.

        If ``slot`` is None, drops the ``cursor_slot`` or, if that's empty,
        the currently held item (``active_slot``).

        Args:
            slot (Optional[Slot]): The dropped slot. Can be None, integer,
                                   or ``Slot`` instance.

        Returns:
            int: The action ID of the click
        """
        if slot is None:
            if self.cursor_slot.is_empty:
                slot = self.active_slot
            else:
                slot = self.cursor_slot
        elif isinstance(slot, int):  # also allow slot nr
            slot = self.window.slots[slot]
        if slot == self.cursor_slot:
            # dropping items from cursor is done via normal click
            return self.click_slot(self.cursor_slot, not drop_stack)
        return self.send_click(windows.DropClick(slot, drop_stack))

    def close_window(self):
        # TODO does server send close window, or should we close window now?
        # for now, we just call handle_close_window() on 'PLAY>Close Window'
        self._net.push_packet('PLAY>Close Window',
                              {'window_id': self.window.window_id})

    def creative_set_slot(self, slot_nr=None, slot_dict=None, slot=None):
        # TODO test
        self._net.push_packet('PLAY>Creative Inventory Action', {
            'slot': slot_nr or slot.slot_nr,
            'clicked_item': slot_dict or slot.get_dict(),
        })

    @property
    def active_slot(self):
        return self.window.hotbar_slots[self.active_slot_nr]

    @property
    def inv_slots_preferred(self):
        """
        List of all available inventory slots in the preferred search order.
        Does not include the additional slots from the open window.

        1. active slot
        2. remainder of the hotbar
        3. remainder of the persistent inventory
        """
        slots = [self.active_slot]
        slots.extend(slot for slot in self.window.hotbar_slots
                     if slot != self.active_slot)
        slots.extend(self.window.inventory_slots)
        return slots


@pl_announce('Inventory')
class InventoryPlugin(PluginBase):
    requires = ('Event', 'Net', 'Timers')
    events = {
        'PLAY<Held Item Change': 'handle_held_item_change',
        'PLAY<Set Slot': 'handle_set_slot',
        'PLAY<Window Items': 'handle_window_items',
        'PLAY<Window Property': 'handle_window_prop',
        'PLAY<Confirm Transaction': 'handle_confirm_transaction',
        'PLAY<Open Window': 'handle_open_window',
        'PLAY<Close Window': 'handle_close_window',
        # also register to serverbound, as server
        # does not send Close Window when we do
        'PLAY>Close Window': 'handle_close_window',
    }

    def __init__(self, ploader, settings):
        super(InventoryPlugin, self).__init__(ploader, settings)

        self.inventory = InventoryCore(self.net, self.send_click)
        ploader.provides('Inventory', self.inventory)

        # click sending

        # start at 1 so bool(action_id) is
        # False only for None, see send_click
        self.action_id = 1

        # stores the last click action for confirmation
        self.last_click = None

        # to know when the inventory got synced with server
        self.is_synchronized = False

        # emit inv_open_window when the inventory is loaded
        self.event.reg_event_handler('inventory_synced', self.emit_open_window)

    def emit_open_window(self, *_):
        self.event.emit('inventory_open_window',
                        {'window': self.inventory.window})
        return EVENT_UNREGISTER  # unregister this handler

    def handle_held_item_change(self, event, packet):
        self.inventory.active_slot_nr = packet.data['slot']
        self.event.emit('inventory_held_item_change', packet.data)

    def handle_open_window(self, event, packet):
        inv_type = windows.inv_types[packet.data['inv_type']]
        self.inventory.window = inv_type(
            persistent_slots=self.inventory.window.slots, **packet.data)
        self.is_synchronized = False
        self.event.reg_event_handler('inventory_synced', self.emit_open_window)

    def handle_close_window(self, event, packet):
        closed_window = self.inventory.window
        self.inventory.window = windows.PlayerWindow(
            persistent_slots=closed_window.slots)
        self.event.emit('inventory_close_window', {'window': closed_window})

    def handle_set_slot(self, event, packet):
        data = packet.data
        self.set_slot(data['window_id'], data['slot'], data['slot_data'])

        if not self.is_synchronized \
                and data['slot'] == constants.INV_SLOT_NR_CURSOR \
                and data['window_id'] == constants.INV_WINID_CURSOR:
            # all slots received, inventory state synchronized with server
            self.is_synchronized = True
            self.event.emit('inventory_synced', {})

    def handle_window_items(self, event, packet):
        window_id = packet.data['window_id']
        for slot_nr, slot_data in enumerate(packet.data['slots']):
            self.set_slot(window_id, slot_nr, slot_data)

    def set_slot(self, window_id, slot_nr, slot_data):
        inv = self.inventory
        if window_id != inv.window.window_id \
                and window_id == constants.INV_WINID_PLAYER:
            # server did not close the open window
            # before adressing the player inventory
            self.handle_close_window(None, None)
        elif window_id > inv.window.window_id:
            # server did not send the Open Window packet yet
            return  # assume window will be empty TODO defer the set_slot?

        if window_id == constants.INV_WINID_CURSOR \
                and slot_nr == constants.INV_SLOT_NR_CURSOR:
            slot = inv.cursor_slot = windows.SlotCursor(**slot_data)
        elif window_id == inv.window.window_id:
            slot = inv.window.slots[slot_nr] = windows.Slot(
                inv.window, slot_nr, **slot_data)
        else:
            raise ValueError(
                'Unexpected slot_nr (%i) or window ID (%i instead of %i)'
                % (slot_nr, window_id, inv.window.window_id))

        self.emit_set_slot(slot)

    def emit_set_slot(self, slot):
        self.event.emit('inventory_set_slot', {'slot': slot})

    def handle_window_prop(self, event, packet):
        window = self.inventory.window
        prop_id = packet.data['property']
        prop_name = window.inv_data['properties'][prop_id]
        window.properties[prop_id] = packet.data['value']
        self.event.emit('inventory_win_prop', {
            'window_id': packet.data['window_id'],
            'property_name': prop_name,
            'property_id': prop_id,
            'value': packet.data['value'],
        })

    def handle_confirm_transaction(self, event, packet):
        click = self.last_click
        self.last_click = None
        action_id = packet.data['action']
        accepted = packet.data['accepted']

        def emit_click_response(*_):
            self.event.emit('inventory_click_response', {
                'action_id': action_id,
                'accepted': accepted,
                'click': click,
            })
            return EVENT_UNREGISTER  # unregister this handler

        if accepted:
            # TODO check if the wrong window/action ID was confirmed,
            # never occured during testing update inventory, because 1.8
            # server does not send slot updates after successful clicks
            click.on_success(self.inventory, self.emit_set_slot)
            emit_click_response()
        else:  # click not accepted
            self.is_synchronized = False
            # confirm that we received this packet
            packet.new_ident('PLAY>Confirm Transaction')
            self.net.push(packet)
            # 1.8 server will re-send all slots now
            self.event.reg_event_handler('inventory_synced',
                                         emit_click_response)

    def send_click(self, click):
        """
        Sends a click to the server if the previous click has been confirmed.

        Args:
            click (BaseClick): The click to send.

        Returns:
            the click's action ID if the click could be sent,
            None if the previous click has not been received and confirmed yet.
        """
        # only send if previous click got confirmed
        if self.last_click:
            return None
        inv = self.inventory
        packet = click.get_packet(inv)
        try:
            craft_result_slot = inv.window.craft_result_slot.slot_nr
            if packet['slot'] == craft_result_slot:
                # send wrong click to update inventory after crafting
                packet['clicked_item'] = {'id': -1}
        except AttributeError:
            pass  # not crafting
        self.action_id += 1
        packet['window_id'] = inv.window.window_id
        packet['action'] = self.action_id
        self.last_click = click
        self.net.push_packet('PLAY>Click Window', packet)
        return self.action_id
