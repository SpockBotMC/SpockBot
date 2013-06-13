"""

This module intends to give an overview of how chunks are packed and unpacked
in the minecraft smp protocol. It provides a simple world manager that makes
use of the smp packet format internally.

Last updated for 1.4.6

"""

"""

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

Chunk Coords * 16 + Block Coords gives you the actual position of the block in the world

"""


import array
import struct
import zlib

try:
	from cStringIO import StringIO
except ImportError:
	from StringIO import StringIO

class BiomeData:
	""" A 16x16 array stored in each ChunkColumn. """
	data = None
	
	def fill(self):
		if not self.data:
			self.data = array.array('B', [0]*256)
	
	def unpack(self, buff):
		self.data = array.array('B', buff.read(256))
	
	def pack(self):
		return self.data.tostring()
	
	def get(self, x, z):
		self.fill()
		return self.data[x + z * 16]
	
	def put(self, x, z, d):
		self.fill()
		self.data[x + z * 16] = d


class ChunkData:
	""" A 16x16x16 array for storing block IDs. """
	length = 16*16*16
	data   = None
	
	def fill(self):
		if not self.data:
			self.data = array.array('B', [0]*self.length)
	
	def unpack(self, buff):
		self.data = array.array('B', buff.read(self.length))
	
	def pack(self):
		self.fill()
		return self.data.tostring()
	
	def get(self, x, y, z):
		self.fill()
		return self.data[x + ((y * 16) + z) * 16]
	
	def put(self, x, y, z, data):
		self.fill()
		self.data[x + ((y * 16) + z) * 16] = data


class ChunkDataNibble(ChunkData):
	""" A 16x16x8 array for storing metadata, light or add. Each array element
	contains two 4-bit elements. """
	length = 16*16*8
	
	def get(self, x, y, z):
		self.fill()
		x, r = divmod(x, 2)
		i = x + ((y * 16) + z) * 16

		if r == 0:
			return self.data[i] >> 4
		else:
			return self.data[i] & 0x0F

	def put(self, x, y, z, data):
		self.fill()
		x, r = divmod(x, 2)
		i = x + ((y * 16) + z) * 16
		
		if r == 0:
			self.data[i] = (self.data[i] & 0x0F) | ((data & 0x0F) << 4)
		else:
			self.data[i] = (self.data[i] & 0xF0) | (data & 0x0F)


class Chunk(dict):
	""" Collates the various data arrays """
	
	def __init__(self):
		self['block_data']  = ChunkData()
		self['block_meta']  = ChunkDataNibble()
		self['block_add']   = ChunkDataNibble()
		self['light_block'] = ChunkDataNibble()
		self['light_sky']   = ChunkDataNibble()


class ChunkColumn:
	""" Initialised chunks are a Chunk, otherwise None. """
	
	def __init__(self):
		self.chunks = [None]*16
		self.biome  = BiomeData()
	
	def unpack(self, buff, mask1, mask2, skylight=True, ground_up=True):
		#In the protocol, each section is packed sequentially (i.e. attributes
		#pertaining to the same chunk are *not* grouped)
		self.unpack_section(buff, 'block_data',  mask1)
		self.unpack_section(buff, 'block_meta',  mask1)
		self.unpack_section(buff, 'light_block', mask1)
		if skylight:
			self.unpack_section(buff, 'light_sky', mask1)
		self.unpack_section(buff, 'block_add',   mask2)
		if ground_up:
			self.biome.unpack(buff)
		
	def unpack_section(self, buff, section, mask):
		#Iterate over the bitmask
		for i in range(16):
			if mask & (1 << i):
				if self.chunks[i] == None:
					self.chunks[i] = Chunk()
				self.chunks[i][section].unpack(buff)

class World:
	""" A bunch of ChunkColumns. """
	
	def __init__(self):
		self.columns = {} #chunk columns are address by a tuple (x, z)
	
	def unpack_raw(self, buff, ty):
		return struct.unpack('>'+ty, buff.read(struct.calcsize(ty)))
	
	def unpack_bulk(self, packet):
		skylight = packet.data['sky_light']
		ground_up = True
		
		# Read compressed data
		data = StringIO(zlib.decompress(packet.data['data']))
		
		for bitmap in packet.data['bitmaps']:
			# Read chunk metadata
			x_chunk = bitmap['x']
			z_chunk = bitmap['z']
			mask1 = bitmap['primary_bitmap']
			mask2 = bitmap['secondary_bitmap']
			
			# Grab the relevant column
			key = (x_chunk, z_chunk)
			if key not in self.columns:
				self.columns[key] = ChunkColumn()
			
			# Unpack the chunk column data!
			self.columns[key].unpack(data, mask1, mask2, skylight, ground_up)

	def unpack_column(self, packet):
		x_chunk = packet.data['x_chunk']
		z_chunk = packet.data['z_chunk']
		ground_up = packet.data['ground_up_continuous']
		mask1 = packet.data['primary_bitmap']
		mask2 = packet.data['secondary_bitmap']
		data = StringIO(zlib.decompress(packet.data['data']))
		skylight = True

		key = (x_chunk, z_chunk)
		if key not in self.columns:
			self.columns[key] = ChunkColumn()

		self.columns[key].unpack(data, mask1, mask2, skylight, ground_up)
	
	def get(self, x, y, z, key):
		x, rx = divmod(x, 16)
		y, ry = divmod(y, 16)
		z, rz = divmod(z, 16)
		
		if not (x,z) in self.columns:
			return 0
		column = self.columns[(x,z)]
		
		chunk = column.chunks[y]
		if chunk == None:
			return 0
		
		return chunk[key].get(rx,ry,rz)
	
	def put(self, x, y, z, key, data):
		x, rx = divmod(x, 16)
		y, ry = divmod(y, 16)
		z, rz = divmod(z, 16)
		
		if (x,z) in self.columns:
			column = self.columns[(x,z)]
		else:
			column = ChunkColumn()
			self.columns[(x,z)] = column
		
		chunk = column.chunks[y]
		if chunk == None:
			chunk = Chunk()
			column.chunks[y] = chunk
		
		chunk[key].put(rx,ry,rz,data)
	
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
		
		return column.biome.put(rx, rz, data)