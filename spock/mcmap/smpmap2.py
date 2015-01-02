#Eventually put advanced map functions here

class MapBlock:
	def __init__(self, block_id = 0, meta = 0):
		self.block_id = block_id
		self.meta = meta
		self.light = 0
		self.sky_light = 0
		self.block_light = 0
		self.biome = 0

	#Needs to do proper light calc based on time_of_day
	def calc_light(self, time):
		self.light = max(self.block_light, self.sky_light)
