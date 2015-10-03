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

from spockbot.mcp.datautils import BoundBuffer

DIMENSION_NETHER = -0x01
DIMENSION_OVERWOLD = 0x00
DIMENSION_END = 0x01


def mapshort2id(data):
    return data >> 4, data & 0x0F


class ChunkData(object):
    length = 16 * 16 * 16
    ty = 'B'
    data = None

    def fill(self):
        if not self.data:
            self.data = array.array(self.ty, [0] * self.length)

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
    length = 16 * 16
    data = None

    def get(self, x, z):
        self.fill()
        return self.data[x + z * 16]

    def set(self, x, z, d):
        self.fill()
        self.data[x + z * 16] = d


class ChunkDataShort(ChunkData):
    """ A 16x16x16 array for storing block IDs/Metadata. """
    length = 16 * 16 * 16 * 2
    ty = 'H'


class ChunkDataNibble(ChunkData):
    """ A 16x16x8 array for storing metadata, light or add. Each array element
    contains two 4-bit elements. """
    length = 16 * 16 * 8

    def get(self, x, y, z):
        self.fill()
        x, r = divmod(x, 2)
        i = x + ((y * 16) + z) * 16
        return self.data[i] & 0x0F if r else self.data[i] >> 4

    def set(self, x, y, z, data):
        self.fill()
        x, r = divmod(x, 2)
        i = x + ((y * 16) + z) * 16
        if r:
            self.data[i] = (self.data[i] & 0xF0) | (data & 0x0F)
        else:
            self.data[i] = (self.data[i] & 0x0F) | ((data & 0x0F) << 4)


class Chunk(object):
    def __init__(self):
        self.block_data = ChunkDataShort()
        self.light_block = ChunkDataNibble()
        self.light_sky = ChunkDataNibble()


class ChunkColumn(object):
    def __init__(self):
        self.chunks = [None] * 16
        self.biome = BiomeData()

    def unpack(self, buff, mask, skylight=True, continuous=True):
        # In the protocol, each section is packed sequentially (i.e. attributes
        # pertaining to the same chunk are *not* grouped)
        chunk_idx = [i for i in range(16) if mask & (1 << i)]
        for i in chunk_idx:
            if self.chunks[i] is None:
                self.chunks[i] = Chunk()
            self.chunks[i].block_data.unpack(buff)
        for i in chunk_idx:
            self.chunks[i].light_block.unpack(buff)
        if skylight:
            for i in chunk_idx:
                self.chunks[i].light_sky.unpack(buff)
        if continuous:
            self.biome.unpack(buff)


class Dimension(object):
    """ A bunch of ChunkColumns. """

    def __init__(self, dimension):
        self.dimension = dimension
        self.columns = {}  # chunk columns are address by a tuple (x, z)

    def unpack_bulk(self, data):
        bbuff = BoundBuffer(data['data'])
        skylight = data['sky_light']
        for meta in data['metadata']:
            key = meta['chunk_x'], meta['chunk_z']
            if key not in self.columns:
                self.columns[key] = ChunkColumn()
            self.columns[key].unpack(bbuff, meta['primary_bitmap'], skylight)

    def unpack_column(self, data):
        bbuff = BoundBuffer(data['data'])
        skylight = True if self.dimension == DIMENSION_OVERWOLD else False
        key = data['chunk_x'], data['chunk_z']
        if key not in self.columns:
            self.columns[key] = ChunkColumn()
        self.columns[key].unpack(
            bbuff, data['primary_bitmap'], skylight, data['continuous']
        )

    def get_block(self, x, y, z):
        x, y, z = int(x), int(y), int(z)  # Damn you python2
        x, rx = divmod(x, 16)
        y, ry = divmod(y, 16)
        z, rz = divmod(z, 16)

        if (x, z) not in self.columns or y > 0x0F:
            return 0, 0
        chunk = self.columns[(x, z)].chunks[y]
        if chunk is None:
            return 0, 0
        data = chunk.block_data.get(rx, ry, rz)
        return data >> 4, data & 0x0F

    def set_block(self, x, y, z, block_id=None, meta=None, data=None):
        x, rx = divmod(x, 16)
        y, ry = divmod(y, 16)
        z, rz = divmod(z, 16)

        if y > 0x0F:
            return
        if (x, z) in self.columns:
            column = self.columns[(x, z)]
        else:
            column = ChunkColumn()
            self.columns[(x, z)] = column
        chunk = column.chunks[y]
        if chunk is None:
            chunk = Chunk()
            column.chunks[y] = chunk

        if data is None:
            data = (block_id << 4) | (meta & 0x0F)
        chunk.block_data.set(rx, ry, rz, data)

    def get_light(self, x, y, z):
        x, rx = divmod(x, 16)
        y, ry = divmod(y, 16)
        z, rz = divmod(z, 16)

        if (x, z) not in self.columns or y > 0x0F:
            return 0, 0
        chunk = self.columns[(x, z)].chunks[y]
        if chunk is None:
            return 0, 0
        return chunk.light_block.get(rx, ry, rz), chunk.light_sky.get(rx, ry,
                                                                      rz)

    def set_light(self, x, y, z, light_block=None, light_sky=None):
        x, rx = divmod(x, 16)
        y, ry = divmod(y, 16)
        z, rz = divmod(z, 16)

        if y > 0x0F:
            return
        if (x, z) in self.columns:
            column = self.columns[(x, z)]
        else:
            column = ChunkColumn()
            self.columns[(x, z)] = column
        chunk = column.chunks[y]
        if chunk is None:
            chunk = Chunk()
            column.chunks[y] = chunk

        if light_block is not None:
            chunk.light_block.set(rx, ry, rz, light_block & 0xF)
        if light_sky is not None:
            chunk.light_sky.set(rx, ry, rz, light_sky & 0xF)

    def get_biome(self, x, z):
        x, rx = divmod(x, 16)
        z, rz = divmod(z, 16)

        if (x, z) not in self.columns:
            return 0

        return self.columns[(x, z)].biome.get(rx, rz)

    def set_biome(self, x, z, data):
        x, rx = divmod(x, 16)
        z, rz = divmod(z, 16)

        if (x, z) in self.columns:
            column = self.columns[(x, z)]
        else:
            column = ChunkColumn()
            self.columns[(x, z)] = column

        return column.biome.set(rx, rz, data)
