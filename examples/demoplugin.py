#TODO: Make this cooler
class DemoPlugin:
	def __init__(self, ploader, settings):
		pl_loader.reg_event_handler((0x03, 0x0D, 0xC9 0xFF), self.print_packets)

	def print_packets(self, name, packet):
		print(packet)