"""
An example plugin for spockbot

Demonstrates the following functionality:
- Receiving chat messages
- Sending chat commands
- Using inventory
- Moving to location
- Triggering a periodic event using a timer
- Registering for an event upon startup
- Placing blocks
- Reading blocks
"""
import logging

# Import any modules that you need in your plugin
from spockbot.mcdata import blocks
from spockbot.plugins.base import PluginBase, pl_announce
from spockbot.plugins.tools.event import EVENT_UNREGISTER
from spockbot.vector import Vector3

__author__ = 'Cosmo Harrigan, Morgan Creekmore'

logger = logging.getLogger('spockbot')

# The bot will walk to this starting position. Set it to a sensible
# location for your world file. The format is: (x, y, z)
TARGET_COORDINATES = Vector3(10, 2, 10)


# Required class decorator
@pl_announce('ExamplePlugin')
class ExamplePlugin(PluginBase):
    # Require other plugins that you want use later in the plugin
    requires = ('Movement', 'Timers', 'World', 'ClientInfo', 'Inventory',
                'Interact', 'Chat')
    # Example of registering an event handler
    # Packet event types are enumerated here:
    #  https://github.com/SpockBotMC/SpockBot/blob/master/spockbot/mcp
    # /mcdata.py#L213
    # There are other events that can be used that are emitted by other plugins
    events = {
        # This event will be triggered when a chat message is received
        # from the server
        'PLAY<Chat Message': 'chat_event_handler',
        # This event will be triggered after authentication when the bot
        # joins the game
        'client_join_game': 'perform_initial_actions',
        # This event is triggered once the inventory plugin has the
        # full inventory
        'inventory_synced': 'hold_block',
    }

    def __init__(self, ploader, settings):
        # Used to init the PluginBase
        super(ExamplePlugin, self).__init__(ploader, settings)

        # Example of registering a timer that triggers a method periodically
        frequency = 5  # Number of seconds between triggers
        self.timers.reg_event_timer(frequency, self.periodic_event_handler)

    def perform_initial_actions(self, name, data):
        """Sends a chat message, then moves to target coordinates."""

        # Send a chat message
        self.chat.chat('Bot active')

        # Walk to target coordinates
        self.movement.move_to(*TARGET_COORDINATES)

    def chat_event_handler(self, name, data):
        """Called when a chat message occurs in the game"""
        logger.info('Chat message received: {0}'.format(data))

    def hold_block(self, name, data):
        # Search the hotbar for cobblestone
        slot = self.inventory.find_slot(4, self.inventory.window.hotbar_slots)
        # Switch to slot with cobblestone
        if slot is not None:
            self.inventory.select_active_slot(slot)
        # Switch to first slot because there is no cobblestone in hotbar
        else:
            self.inventory.select_active_slot(0)
        # Return EVENT_UNREGISTER to unregister the event handler
        return EVENT_UNREGISTER

    def periodic_event_handler(self):
        """Triggered every 5 seconds by a timer"""

        logger.info('My position: {0} pitch: {1} yaw: {2}'.format(
            self.clientinfo.position,
            self.clientinfo.position.pitch,
            self.clientinfo.position.yaw))

        # Place a block in front of the player
        self.interact.place_block(
            self.clientinfo.position + Vector3(-1, 0, -1))

        # Read a block under the player
        block_pos = self.clientinfo.position.floor()
        block_id, meta = self.world.get_block(*block_pos)
        block_at = blocks.get_block(block_id, meta)
        self.chat.chat('Found block %s at %s' % (
            block_at.display_name, block_pos))
