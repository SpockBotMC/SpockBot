"""
Sample plugin
"""

#TODO: Make this cooler
class DemoPlugin:
	def __init__(self, ploader, settings):
		#Login Success
		ploader.reg_event_handler(
			"LOGIN<Login Success",
			self.print_packets
		)
		#Chat Message
		ploader.reg_event_handler(
			"PLAY<Chat Message", 
			self.print_packets
		)
		#Player List Item
		ploader.reg_event_handler(
			"PLAY<Player List Item",
			self.print_packets
		)

	def print_packets(self, name, packet):
		print(packet)