"""
Used for storing map data

Chunks are packed in X, Z, Y order
The array walks down X, every 16 elements you enter a new Z-level
ex.
[0] - [15] are X = 0-15, Z = 0, Y = 0
[16] - [31] are X = 0-15, Z = 1, Y = 0
and so on

Every 256 elements you enter a new Y-level
ex.
[0]-[255] are X = 0-15, Z = 0-15, Y = 0
[256]-[511] are X = 0-15, Z = 0-15, Y = 1
and so on

"""

import array
import struct
from spock import utils

DIMENSION_NETHER   = -0x01
DIMENSION_OVERWOLD =  0x00
DIMENSION_END      =  0x01

class ChunkData:
    length = 16*16*16
    ty = 'B'
    data   = None

    def fill(self):
        if not self.data:
            self.data = array.array(self.ty, [0]*self.length)

    def unpack(self, buff):
        self.data = array.array(self.ty, buff.read(self.length))

    def pack(self):
        self.fill()
        return self.data.tobytes()

    def get(self, x, y, z):
        self.fill()
        return self.data[x + ((y * 16) + z) * 16]

    def set(self, x, y, z, data):
        self.fill()
        self.data[x + ((y * 16) + z) * 16] = data

class BiomeData(ChunkData):
    """ A 16x16 array stored in each ChunkColumn. """
    length = 16*16
    data = None

    def get(self, x, z):
        self.fill()
        return self.data[x + z * 16]

    def set(self, x, z, d):
        self.fill()
        self.data[x + z * 16] = d

class ChunkDataShort(ChunkData):
    """ A 16x16x16 array for storing block IDs/Metadata. """
    length = 16*16*16*2
    ty = 'H'

class ChunkDataNibble(ChunkData):
    """ A 16x16x8 array for storing metadata, light or add. Each array element
    contains two 4-bit elements. """
    length = 16*16*8

    def get(self, x, y, z):
        self.fill()
        x, r = divmod(x, 2)
        i = x + ((y * 16) + z) * 16
        if r:
            return self.data[i] & 0x0F
        else:
            return self.data[i] >> 4

    def set(self, x, y, z, data):
        self.fill()
        x, r = divmod(x, 2)
        i = x + ((y * 16) + z) * 16
        if r:
            self.data[i] = (self.data[i] & 0xF0) | (data & 0x0F)
        else:
            self.data[i] = (self.data[i] & 0x0F) | ((data & 0x0F) << 4)

class Chunk:
    def __init__(self):
        self.block_data = ChunkDataShort()
        self.light_block = ChunkDataNibble()
        self.light_sky = ChunkDataNibble()


class ChunkColumn:
    def __init__(self):
        self.chunks = [None]*16
        self.biome = BiomeData()

    def unpack(self, buff, mask, skylight=True, continuous=True):
        #In the protocol, each section is packed sequentially (i.e. attributes
        #pertaining to the same chunk are *not* grouped)
        self.unpack_block_data(buff, mask)
        self.unpack_light_block(buff, mask)
        if skylight:
            self.unpack_light_sky(buff, mask)
        if continuous:
            self.biome.unpack(buff)

    def unpack_block_data(self, buff, mask):
        for i in range(16):
            if mask&(1<<i):
                if self.chunks[i] == None:
                    self.chunks[i] = Chunk()
                self.chunks[i].block_data.unpack(buff)

    def unpack_light_block(self, buff, mask):
        for i in range(16):
            if mask&(1<<i):
                if self.chunks[i] == None:
                    self.chunks[i] = Chunk()
                self.chunks[i].light_block.unpack(buff)

    def unpack_light_sky(self, buff, mask):
        for i in range(16):
            if mask&(1<<i):
                if self.chunks[i] == None:
                    self.chunks[i] = Chunk()
                self.chunks[i].light_sky.unpack(buff)

class Dimension(object):
    """ A bunch of ChunkColumns. """

    def __init__(self, dimension):
        self.dimension = dimension
        self.columns = {} #chunk columns are address by a tuple (x, z)

    def unpack_bulk(self, data):
        skylight = data['sky_light']
        bbuff = utils.BoundBuffer(data['data'])
        for meta in data['metadata']:
            # Read chunk metadata
            x_chunk = meta['chunk_x']
            z_chunk = meta['chunk_z']
            mask = meta['primary_bitmap']

            # Grab the relevant column
            key = (x_chunk, z_chunk)
            if key not in self.columns:
                self.columns[key] = ChunkColumn()

            # Unpack the chunk column data
            self.columns[key].unpack(bbuff, mask, skylight)

    def unpack_column(self, data):
        x_chunk = data['chunk_x']
        z_chunk = data['chunk_z']
        mask = data['primary_bitmap']
        continuous = data['continuous']
        bbuff = utils.BoundBuffer(data['data'])
        if self.dimension == DIMENSION_OVERWOLD:
            skylight = True
        else:
            skylight = False

        key = (x_chunk, z_chunk)
        if key not in self.columns:
            self.columns[key] = ChunkColumn()

        self.columns[key].unpack(bbuff, mask, skylight, continuous)

    def get_block(self, x, y, z):
        x, y, z = int(x), int(y), int(z) #Damn you python2
        x, rx = divmod(x, 16)
        y, ry = divmod(y, 16)
        z, rz = divmod(z, 16)

        if (x, z) not in self.columns or y > 0x0F:
            return 0, 0
        column = self.columns[(x,z)]
        chunk = column.chunks[y]
        if chunk == None:
            return 0, 0

        data = chunk.block_data.get(rx,ry,rz)
        return data>>4, data&0x0F

    def set_block(self, x, y, z, block_id = None, meta = None, data = None):
        x, rx = divmod(x, 16)
        y, ry = divmod(y, 16)
        z, rz = divmod(z, 16)

        if y > 0x0F:
            return
        if (x,z) in self.columns:
            column = self.columns[(x,z)]
        else:
            column = ChunkColumn()
            self.columns[(x,z)] = column
        chunk = column.chunks[y]
        if chunk == None:
            chunk = Chunk()
            column.chunks[y] = chunk

        if data == None:
            data = (block_id<<4)|(meta&0x0F)
        chunk.block_data.set(rx, ry, rz, data)

    def get_light(self, x, y, z):
        x, rx = divmod(x, 16)
        y, ry = divmod(y, 16)
        z, rz = divmod(z, 16)

        if (x, z) not in self.columns or y > 0x0F:
            return 0, 0
        column = self.columns[(x,z)]
        chunk = column.chunks[y]
        if chunk == None:
            return 0, 0

        return chunk.light_block.get(rx,ry,rz), chunk.light_sky.get(rx,ry,rz)

    def set_light(self, x, y, z, light_block = None, light_sky = None):
        x, rx = divmod(x, 16)
        y, ry = divmod(y, 16)
        z, rz = divmod(z, 16)

        if y > 0x0F:
            return
        if (x,z) in self.columns:
            column = self.columns[(x, z)]
        else:
            column = ChunkColumn()
            self.columns[(x, z)] = column
        chunk = column.chunks[y]
        if chunk == None:
            chunk = Chunk()
            column.chunks[y] = chunk

        if light_block != None:
            chunk.light_block.set(rx, ry, rz, light_block&0xF)
        if light_sky != None:
            chunk.light_sky.set(rx, ry, rz, light_sky&0xF)

    def get_biome(self, x, z):
        x, rx = divmod(x, 16)
        z, rz = divmod(z, 16)

        if (x,z) not in self.columns:
            return 0

        return self.columns[(x,z)].biome.get(rx, rz)

    def set_biome(self, x, z, data):
        x, rx = divmod(x, 16)
        z, rz = divmod(z, 16)

        if (x,z) in self.columns:
            column = self.columns[(x,z)]
        else:
            column = ChunkColumn()
            self.columns[(x,z)] = column

        return column.biome.set(rx, rz, data)
