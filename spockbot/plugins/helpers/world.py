"""
Provides a very raw (but very fast) world map for use by plugins. Plugins
interested in a more comprehensive world map view can use mcp.mapdata to
interpret blocks and their metadata more comprehensively. Planned to provide
light level interpretation based on sky light and time of day
"""

from spockbot.mcdata import constants as const
from spockbot.plugins.base import PluginBase, pl_announce
from spockbot.plugins.tools import smpmap


class WorldData(smpmap.Dimension):
    def __init__(self, dimension=const.SMP_OVERWORLD):
        super(WorldData, self).__init__(dimension)
        self.age = 0
        self.time_of_day = 0

    def update_time(self, data):
        self.age = data['world_age']
        self.time_of_day = data['time_of_day']

    def new_dimension(self, dimension):
        super(WorldData, self).__init__(dimension)

    def reset(self):
        self.__init__(self.dimension)


@pl_announce('World')
class WorldPlugin(PluginBase):
    requires = 'Event'
    events = {
        'PLAY<Join Game': 'handle_new_dimension',
        'PLAY<Respawn': 'handle_new_dimension',
        'PLAY<Time Update': 'handle_time_update',
        'PLAY<Chunk Data': 'handle_chunk_data',
        'PLAY<Multi Block Change': 'handle_multi_block_change',
        'PLAY<Block Change': 'handle_block_change',
        'PLAY<Map Chunk Bulk': 'handle_map_chunk_bulk',
        'net_disconnect': 'handle_disconnect',
    }

    def __init__(self, ploader, settings):
        super(WorldPlugin, self).__init__(ploader, settings)
        self.world = WorldData()
        ploader.provides('World', self.world)

    def handle_time_update(self, name, packet):
        """Time Update - Update World Time"""
        self.world.update_time(packet.data)
        self.event.emit('world_time_update', packet.data)

    def handle_new_dimension(self, name, packet):
        """Join Game/Respawn - New Dimension"""
        self.world.new_dimension(packet.data['dimension'])
        self.event.emit('world_new_dimension', packet.data['dimension'])

    def handle_chunk_data(self, name, packet):
        """Chunk Data - Update World state"""
        self.world.unpack_column(packet.data)

    def handle_multi_block_change(self, name, packet):
        """Multi Block Change - Update multiple blocks"""
        chunk_x = packet.data['chunk_x'] * 16
        chunk_z = packet.data['chunk_z'] * 16
        for block in packet.data['blocks']:
            x = block['x'] + chunk_x
            z = block['z'] + chunk_z
            y = block['y']
            self.world.set_block(x, y, z, data=block['block_data'])
            self.event.emit('world_block_update', {
                'location': {
                    'x': x,
                    'y': y,
                    'z': z,
                },
                'block_data': block['block_data'],
            })

    def handle_block_change(self, name, packet):
        """Block Change - Update a single block"""
        p = packet.data['location']
        block_data = packet.data['block_data']
        self.world.set_block(p['x'], p['y'], p['z'], data=block_data)
        self.event.emit('world_block_update', packet.data)

    def handle_map_chunk_bulk(self, name, packet):
        """Map Chunk Bulk - Update World state"""
        self.world.unpack_bulk(packet.data)

    def handle_disconnect(self, name, data):
        self.world.reset()
        self.event.emit('world_reset')
