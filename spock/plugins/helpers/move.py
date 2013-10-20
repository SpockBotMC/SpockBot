class MovementPlugin:
	def __init__(self, ploader, settings):
		self.client = ploader.requires('Client')
		self.world = ploader.requires('World')