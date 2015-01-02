from spock.mcp import mcdata, mcpacket

class MovementPlugin:
	def __init__(self, ploader, settings):
		self.net = ploader.requires('Net')
		ploader.reg_event_handler(
			(mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x08), 
			self.handle_position_look
		)
		ploader.reg_event_handler(
			(mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x07), 
			self.handle_respawn
		)
		ploader.reg_event_handler('client_tick', self.client_tick)
		#TODO: use clientInfo plugin instead
		self.position = {
			'x': 0,
			'y': 0,
			'z': 0,
			'yaw': 0,
			'pitch': 0,
			'on_ground': False,
		}

	def handle_position_look(self, name, packet):
		self.position['x'] = packet.data['x']
		self.position['y'] = packet.data['y']
		self.position['z'] = packet.data['z']
		self.position['pitch'] = packet.data['pitch']
		self.position['pitch'] = packet.data['yaw']

		self.net.push(mcpacket.Packet(
			ident = (mcdata.PLAY_STATE, mcdata.CLIENT_TO_SERVER, 0x06),
			#TODO: check flags to see if Absolute vs Relative
			data = {
				'x': self.position['x'],
				'y': self.position['y'],
				'z': self.position['z'],
				'pitch': self.position['pitch'],
				'yaw': self.position['yaw'],
				'on_ground': True
			}
		))

	def client_tick(self, name, data):
		self.net.push(mcpacket.Packet(
			ident = (mcdata.PLAY_STATE, mcdata.CLIENT_TO_SERVER, 0x04),
			#TODO: check flags to see if Absolute vs Relative
			data = {
				'x': self.position['x'],
				'y': self.position['y'],
				'z': self.position['z'],
				'on_ground': True
			}
		))

	def handle_respawn(self, name, packet):
		self.net.push(mcpacket.Packet(
			ident = (mcdata.PLAY_STATE, mcdata.CLIENT_TO_SERVER, 0x06),
			#TODO: check flags to see if Absolute vs Relative
			data = {
				'x': self.position['x'],
				'y': self.position['y'],
				'z': self.position['z'],
				'pitch': self.position['pitch'],
				'yaw': self.position['yaw'],
				'on_ground': False
			}
		))

		
		