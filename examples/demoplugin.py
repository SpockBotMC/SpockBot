from spock.mcp import mcdata

#TODO: Make this cooler
class DemoPlugin:
	def __init__(self, ploader, settings):
		#Login Success
		ploader.reg_event_handler(
			(mcdata.LOGIN_STATE, mcdata.SERVER_TO_CLIENT, 0x02),
			self.print_packets
		)
		#Chat Message
		ploader.reg_event_handler(
			(mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x02), 
			self.print_packets
		)
		#Player List Item
		ploader.reg_event_handler(
			(mcdata.PLAY_STATE, mcdata.SERVER_TO_CLIENT, 0x38),
			self.print_packets
		)

	def print_packets(self, name, packet):
		print(packet)