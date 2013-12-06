import struct
from spock import utils

class MapBlock:
	def __init__(self, base_id = 0, add_id = 0):
		self.base_id = base_id
		self.add_id = add_id
		self.id = self.calc_id()
		self.meta = 0
		self.light = 0
		self.sky_light = 0
		self.block_light = 0
		self.biome = 0

	def calc_id(self):
		self.id = (self.add_id<<8)+self.base_id
		return self.id

	#Needs to do proper light calc based on time_of_day
	def calc_light(self, time):
		self.light = max(self.block_light, self.sky_light)

class Chunk:
	def __init__(self):
		self.length = 16*16*16
		self.time = 0
		self.blocks = [MapBlock() for i in range(self.length)]

	def get(self, x, y, z):
		return self.blocks[x+((y*16)+z)*16]

	def put(self, x, y, z, data):
		block = self.blocks[x+((y*16)+z)*16]
		block.id = data['block_id']
		block.base_id = data['block_id']&0xFF
		block.add_id = data['block_id']>>8
		block.meta = data['metadata']
		return block

	def unpack_data(self, buff):
		for idx, i in enumerate(buff.recv(self.length)):
			self.blocks[idx].id = i
			self.blocks[idx].base_id = i
			self.blocks[idx].add_id = 0

	def unpack_meta(self, buff):
		for idx, i in enumerate(buff.recv(self.length>>1)):
			self.blocks[idx*2].meta = i>>4
			self.blocks[idx*2+1].meta = i&0x0F

	def unpack_add(self, buff):
		for idx, i in enumerate(buff.recv(self.length>>1)):
			self.blocks[idx*2].add_id = i>>4
			self.blocks[idx*2].calc_id()
			self.blocks[idx*2+1].add_id = i&0x0F
			self.blocks[idx*2+1].calc_id()

	def unpack_blight(self, buff):
		for idx, i in enumerate(buff.recv(self.length>>1)):
			self.blocks[idx*2].block_light = i>>4
			self.blocks[idx*2+1].block_light = i&0x0F
		self.update_light()

	def unpack_slight(self, buff):
		for idx, i in enumerate(buff.recv(self.length>>1)):
			self.blocks[idx*2].sky_light = i>>4
			self.blocks[idx*2+1].sky_light = i&0x0F
		self.update_light()

	def unpack_biome(self, x, z, biome_id):
		for y in range(16):
			self.blocks[x+((y*16)+z)*16].biome = biome_id

	def update_light(self, time = None):
		if time: self.time = time
		for block in self.blocks:
			block.calc_light(self.time)

class ChunkColumn:
	def __init__(self):
		self.chunks = [None]*16
		self.biome = [None]*256

	def unpack(self, buff, primary_bitmap, add_bitmap, skylight, continuous):
		primary_mask = []
		add_mask = []
		for i in range(16):
			if primary_bitmap&(1<<i):
				if not self.chunks[i]:
					self.chunks[i] = Chunk()
				primary_mask.append(i)
			if add_bitmap&(1<<i):
				if not self.chunks[i]:
					self.chunks[i] = Chunk()
				add_mask.append(i)

		for i in primary_mask: self.chunks[i].unpack_data(buff)
		for i in primary_mask: self.chunks[i].unpack_meta(buff)
		for i in primary_mask: self.chunks[i].unpack_blight(buff)
		if skylight:
			for i in primary_mask: self.chunks[i].unpack_slight(buff)
		for i in add_mask: self.chunks[i].unpack_add(buff)
		if continuous:
			self.fill(primary_bitmap)
			self.unpack_biome(buff)

	#Adds air-only chunks to the list where no chunk has been provided
	def fill(self, mask):
		for i in range(16):
			if not mask&(1<<i):
				self.chunks[i] = Chunk()

	def unpack_biome(self, buff):
		for idx, biome_id in enumerate(buff.recv(256)):
			self.biome[idx] = biome_id
			for chunk in self.chunks:
				chunk.unpack_biome(idx%16, idx//16, biome_id)

class World:
	def __init__(self):
		self.columns = {}

	def _get_chunk(self, x, y, z):
		chunk_x, rx = divmod(x, 16)
		chunk_y, ry = divmod(y, 16)
		chunk_z, rz = divmod(z, 16)
		key = (chunk_x, chunk_z)
		if not key in self.columns:
			return None
		chunk = self.columns[key].chunks[chunk_y]
		return (chunk, rx, ry, rz) if chunk else None

	def get(self, x, y, z):
		chunk_data = self._get_chunk(x, y, z)
		if not chunk_data:
			return None
		chunk, rx, ry, rz = chunk_data
		return chunk.get(rx, ry, rz)

	def put(self, x, y, z, data):
		chunk_data = self._get_chunk(x, y, z)
		if not chunk_data:
			return None
		chunk, rx, ry, rz = chunk_data
		return chunk.put(rx, ry, rz, data)

	def unpack_column(self, packet_data):
		data = utils.BoundBuffer(packet_data['data'])
		primary_bitmap = packet_data['primary_bitmap']
		add_bitmap = packet_data['add_bitmap']
		continuous = packet_data['continuous']
		key = (packet_data['chunk_x'], packet_data['chunk_z'])
		if key not in self.columns:
			self.columns[key] = ChunkColumn()

		# Calculate the size of the packet without skylight
		# If calculated size is less than actual size, skylight was sent
		# Important because Nether does not send skylight data
		primary_count = 0
		add_count = 0
		for i in range(16):
			if primary_bitmap&(1<<i): primary_count += 1
			if add_bitmap&(1<<i): add_count += 1
		size_calc = primary_count*((16*16*16)+(16*16*8)*2)
		size_calc += add_count*(16*16*8)
		if continuous: size_calc += 16*16
		skylight = False if size_calc == len(data) else True
		if skylight:
			size_calc += primary_count*(16*16*8)
			assert(size_calc == len(data))

		self.columns[key].unpack(
			data, primary_bitmap, add_bitmap, skylight, continuous
		)
		return key

	def unpack_bulk(self, packet_data):
		keys = []
		data = utils.BoundBuffer(packet_data['data'])
		skylight = packet_data['sky_light']
		for metadata in packet_data['metadata']:
			key = (metadata['chunk_x'], metadata['chunk_z'])
			keys.append(key)
			if key not in self.columns:
				self.columns[key] = ChunkColumn()
			self.columns[key].unpack(
				data, metadata['primary_bitmap'], 
				metadata['add_bitmap'], skylight, True
			)
		return keys
