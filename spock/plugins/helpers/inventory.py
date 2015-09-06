"""
The Inventory plugin keeps track of the inventory
and provides simple inventory manipulation.
Crafting is not done here.
"""
from spock.mcdata import constants, windows
from spock.mcdata.windows import make_slot_check
from spock.plugins.base import PluginBase
from spock.utils import pl_announce


class InventoryCore(object):
    """ Handles operations with the player inventory. """

    def __init__(self, net_plugin, send_click):
        self._net = net_plugin
        self.send_click = send_click
        self.active_slot_nr = 0
        # the slot that moves with the mouse when clicking a slot
        self.cursor_slot = windows.SlotCursor()
        self.window = windows.PlayerWindow()

    def total_stored(self, wanted, slots=None):
        """
        Calculates the total number of items of that type
        in the current window or given slot range.
        :param wanted: function(Slot) or Slot or itemID or (itemID, metadata)
        """
        if slots is None:
            slots = self.window.slots
        wanted = make_slot_check(wanted)
        return sum(slot.amount for slot in slots if wanted(slot))

    def find_slot(self, wanted, slots=None):
        """
        Returns the first slot containing the item or None if not found.
        Searches the given slots or, if not given,
        active hotbar slot, hotbar, inventory, open window in this order.
        :param wanted: function(Slot) or Slot or itemID or (itemID, metadata)
        """
        for slot in self.find_slots(wanted, slots):
            return slot
        return None

    def find_slots(self, wanted, slots=None):
        """
        Yields all slots containing the item.
        Searches the given slots or, if not given,
        active hotbar slot, hotbar, inventory, open window in this order.
        :param wanted: function(Slot) or Slot or itemID or (itemID, metadata)
        """
        if slots is None:
            slots = self.inv_slots_preferred + self.window.window_slots
        wanted = make_slot_check(wanted)

        for slot in slots:
            if wanted(slot):
                yield slot

    def select_active_slot(self, hotbar_index):
        assert 0 <= hotbar_index < constants.INV_SLOTS_HOTBAR, \
            'Invalid hotbar index'
        if hotbar_index != self.active_slot_nr:
            self.active_slot_nr = hotbar_index
            self._net.push_packet('PLAY>Held Item Change',
                                  {'slot': hotbar_index})

    def click_slot(self, slot, right=False):
        if isinstance(slot, int):  # also allow slot nr
            slot = self.window.slots[slot]
        button = constants.INV_BUTTON_RIGHT \
            if right else constants.INV_BUTTON_LEFT
        return self.send_click(windows.SingleClick(slot, button))

    def drop_slot(self, slot=None, drop_stack=False):
        if slot is None:  # drop held item
            slot = self.active_slot
        elif isinstance(slot, int):  # also allow slot nr
            slot = self.window.slots[slot]
        return self.send_click(windows.DropClick(slot, drop_stack))

    def close_window(self):
        # TODO does server send close window, or should we close window now?
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
    def hotbar_start(self):
        return self.window.hotbar_slots[0].slot_nr

    @property
    def inv_slots_preferred(self):
        """
        The preferred order to search for items or empty slots.
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

    def handle_held_item_change(self, event, packet):
        self.inventory.active_slot_nr = packet.data['slot']
        self.event.emit('inv_held_item_change', packet.data)

    def handle_open_window(self, event, packet):
        inv_type = windows.inv_types[packet.data['inv_type']]
        self.inventory.window = inv_type(
            persistent_slots=self.inventory.window.slots, **packet.data)
        self.event.emit('inv_open_window', {'window': self.inventory.window})

    def handle_close_window(self, event, packet):
        closed_window = self.inventory.window
        self.inventory.window = windows.PlayerWindow(
            persistent_slots=closed_window.slots)
        self.event.emit('inv_close_window', {'window': closed_window})

    def handle_set_slot(self, event, packet):
        self.set_slot(packet.data['window_id'], packet.data['slot'],
                      packet.data['slot_data'])

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
        self.event.emit('inv_set_slot', {'slot': slot})

    def handle_window_prop(self, event, packet):
        self.inventory.window.properties[packet.data['property']] = \
            packet.data['value']
        self.event.emit('inv_win_prop', packet.data)

    def handle_confirm_transaction(self, event, packet):
        click, self.last_click = self.last_click, None
        action_id = packet.data['action']
        accepted = packet.data['accepted']

        def emit_response_event():
            self.event.emit('inv_click_response', {
                'action_id': action_id,
                'accepted': accepted,
                'click': click,
            })

        if accepted:
            # TODO check if the wrong window/action ID was confirmed,
            # never occured during testing update inventory, because 1.8
            # server does not send slot updates after successful clicks
            click.on_success(self.inventory, self.emit_set_slot)
            emit_response_event()
        else:  # click not accepted
            # confirm that we received this packet
            packet.new_ident('PLAY>Confirm Transaction')
            self.net.push(packet)
            # 1.8 server will re-send all slots now
            # TODO are 2 ticks always enough? should wait for expected packets
            self.timers.reg_tick_timer(2, emit_response_event, runs=1)

    def send_click(self, click):
        """
        Returns the click's action ID if the click could be sent,
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
