class SkyNetPlugin:
	def __init__(self, client):
		self.client = client
		client.register_dispatch(log_player, 0xC9)

	def log_player(self, packet):
		player = packet.data['player_name']