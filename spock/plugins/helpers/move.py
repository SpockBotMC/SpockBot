MOVEMENT_TICK = 0.05

class MovementPlugin:
	def __init__(self, ploader, settings):
		self.client = ploader.requires('ClientInfo')
		self.net = ploader.requires('Net')
		self.world = ploader.requires('World')
		self.timer = ploader.requires('Timer')
		self.timer.reg_event_timer(MOVEMENT_TICK, self.send_update, -1)
		ploader.reg_event_handler(
			(0x0A, 0x0B, 0x0C, 0x0D), 
			self.handle_position_update
		)

	def send_update(self):
		self.net.push(mcpacket.Packet(
			ident = 0x0D, 
			data = self.client_info.position
		))

	#Position Update Packets - Reflect new position back to server
	#Clearly something very wrong with this, but no "good" solution
	#jumps to mind. Rework it later
	def handle_position_update(self, name, packet):
		if packet.direction == mcdata.SERVER_TO_CLIENT:
			position = self.client_info.position
			for key, value in packet.data.items():
				position[key] = value
			self.net.push(mcpacket.Packet(
				ident = 0x0D, 
				data = position
			))
		