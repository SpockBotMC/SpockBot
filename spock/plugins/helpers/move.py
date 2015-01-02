from spock.mcp import mcdata, mcpacket

class MovementPlugin:
	def __init__(self, ploader, settings):
		self.net = ploader.requires('Net')
		ploader.reg_event_handler(
			(mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x08), 
			self.handle_position_look
		)

	#Keep Alive - Reflects data back to server
	def handle_position_look(self, name, packet):
		self.net.push(mcpacket.Packet(
			ident = (mcdata.PLAY_STATE, mcdata.CLIENT_TO_SERVER, 0x06),
			#TODO: check flags to see if Absolute vs Relative
			data = {
				'x': packet.data['x'],
				'y': packet.data['y'],
				'z': packet.data['z'],
				'pitch': packet.data['pitch'],
				'yaw': packet.data['yaw'],
				'on_ground': True
			}
		))