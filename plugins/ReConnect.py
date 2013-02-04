class ReConnectPlugin:
	def __init__(self, client):
		self.client = client
		client.register_dispatch(self, 0xFF)