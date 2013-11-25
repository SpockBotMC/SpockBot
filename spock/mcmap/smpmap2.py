import struct
import array

class MapBlock:
	def __init__(self, base_id = 0, add_id = 0):
		self.id = 0
		self.base_id = 0
		self.add_id = 0
		self.light = 0
		self.sky_light = 0
		self.block_light = 0
		self.biome = 0

	def calc_id(self):
		self.id = (add_id<<8)+base_id
		return self.id

	def calc_light(time):
		self.light = max(self.block_light, self.sky_light)

class Chunk:
	def __init__(self):
		self.length = 16*16*16
		self.time = 0
		self.blocks = [MapBlock() for i in range(self.length)]

	def unpack(self, buff, section):
		if section == 'block_data':
			for i in range(self.length):
				self.blocks[i].id = struct.unpack('B', buff.recv(1))
				self.blocks[i].add_id = 0
				self.blocks[i].calc_id()
		else:
			for i in range(self.length>>1):
				data = struct.unpack('B', buff.recv(1))
				high = data>>4
				low = data&0x0F
				if section == 'block_meta':
					self.blocks[i*2].meta = high
					self.blocks[i*2+1].meta = low
				elif section == 'block_add':
					self.blocks[i*2].add_id = high
					self.blocks[i*2].calc_id()
					self.blocks[i*2+1].add_id = low
					self.blocks[i*2+1].calc_id()
				elif section == 'block_light':
					self.blocks[i*2].block_light = high
					self.blocks[i*2+1].block_light = low
				elif section == 'sky_light':
					self.blocks[i*2].sky_light = high
					self.blocks[i*2+1].sky_light = low
		if section == 'block_light' or section == 'skylight':
			self.update_light()

	def update_light(self, time = None):
		if time: self.time = time
		for block in self.blocks:
			block.calc_light(self.time)

	def unpack_biome(self, x, z, biome_id):
		for y in range(16):
			self.blocks[x+((y*16)+z)*16].biome = biome_id

class ChunkColumn:
	def __init__(self):
		self.chunks = [None]*16
		self.biome = [None]*256

	def unpack(self, buff, primary_bitmap, add_bitmap, skylight, continuous):
		self.unpack_section(buff, 'block_data', primary_bitmap)
		self.unpack_section(buff, 'block_meta', primary_bitmap)
		self.unpack_section(buff, 'block_light', primary_bitmap)
		if skylight:
			self.unpack_section(buff, 'sky_light', primary_bitmap)
		self.unpack_section(buff, 'block_add', add_bitmap)
		if continuous:
			self.unpack_biome(buff)

	def unpack_section(self, buff, section, mask):
		for i in range(16):
			if mask&(1<<i):
				if not self.chunks[i]:
					self.chunks[i] = Chunk()
				self.chunks[i].unpack(buff, section)

	def unpack_biome(self, buff):
		for idx, biome_id in enumerate(self.biome):
			biome_id = buff.recv(1)
			for chunk in chunks:
				chunk.unpack_biome(idx%16, idx//16, biome_id)

class World:
	def __init__(self):
		self.columns = {}

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

	def unpack_bulk(self, packet_data):
		data = utils.BoundBuffer(packet_data['data'])
		skylight = packet_data['sky_light']
		for metadata in packet_data['metadata']:
			if key not in self.columns:
				self.columns[key] = ChunkColumn()
			self.columns[key].unpack(
				data, metadata['primary_bitmap'], 
				metadata['add_bitmap'], skylight, True
			)


