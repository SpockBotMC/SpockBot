"""
An example plugin for Spock

Demonstrates the following functionality:
- Receiving chat messages
- Sending chat commands
- Triggering a periodic event using a timer
- Registering for an event upon startup
- Changing bot position and orientation
- Placing blocks
- Reading blocks
"""

__author__ = 'Cosmo Harrigan'

# The bot will teleport to this starting position. Set it to a sensible
# location for your world file. The format is: (x, y, z, y-rot, x-rot)
START_COORDINATES = (10, 2, 10, 0, 0)

import random

# Required import
from spock.utils import pl_announce

# Import any modules that you need in your plugin
from spock.mcp.mcpacket import Packet
from spock.mcmap import mapdata

# Required class decorator
@pl_announce('ExamplePlugin')
class ExamplePlugin:
    def __init__(self, ploader, settings):
        # Load anything that you will use later in the plugin
        # Here are some examples of what you can load:
        self.entities = ploader.requires('Entities')
        self.movement = ploader.requires('Movement')
        self.timers = ploader.requires('Timers')
        self.world = ploader.requires('World')
        self.net = ploader.requires('Net')
        self.clinfo = ploader.requires('ClientInfo')

        # Example of registering an event handler
        # Event types are enumerated here:
        #  https://github.com/SpockBotMC/SpockBot/blob/master/spock/mcp/mcdata.py#L213
        ploader.reg_event_handler('PLAY<Chat Message', self.chat_event_handler)

        # This event will be triggered after authentication when the bot joins the game
        ploader.reg_event_handler("cl_join_game", self.perform_initial_actions)

        # Example of registering a timer that triggers a method periodically
        frequency = 5  # Number of seconds between triggers
        self.timers.reg_event_timer(frequency, self.periodic_event_handler)

    def perform_initial_actions(self, name, data):
        """Teleports the bot to a particular position to start and places a
        block and sends a chat message."""
        # Set position and orientation
        (self.clinfo.position.x,
         self.clinfo.position.y,
         self.clinfo.position.z,
         self.clinfo.position.pitch,
         self.clinfo.position.yaw) = START_COORDINATES

        # Send a chat message
        self.emit_chat_message(msg='Bot active.')

    def chat_event_handler(self, name, data):
        """Called when a chat message occurs in the game"""
        print('Chat message received: {0}'.format(data))

    def periodic_event_handler(self):
        """Triggered every 5 seconds by a timer"""
        print('My position: {0} pitch: {1} yaw: {2}'.format(
            self.clinfo.position,
            self.clinfo.position.pitch,
            self.clinfo.position.yaw))

        # Rotates the bot by 1 degree
        self.clinfo.position.yaw = (self.clinfo.position.yaw + 1) % 360

        # Read a block
        x, y, z = 5, 5, 5
        block_id, meta = self.world.get_block(x, y, z)
        block_placed = mapdata.get_block(block_id, meta)
        print('Before changing the block, the type had id {0} and name {1}.'.format(block_id,
                                                                                    block_placed.name))

        # Place a block (choosing the type randomly from a list of types)
        self.place_block(x, y, z, random.choice(['waterlily', 'red_mushroom', 'brown_mushroom']))

    def emit_chat_message(self, msg):
        """Helper method that sends chat messages or chat commands"""
        self.net.push(Packet(ident='PLAY>Chat Message', data={'message': msg}))

    def place_block(self, x, y, z, block_type):
        """Helper method that places a block by using the 'setblock' chat command"""
        self.emit_chat_message('/setblock {0} {1} {2} {3}'.format(x, y, z, block_type))
