from data import CLIENT_TO_SERVER, SERVER_TO_CLIENT, structs

class Packet:
	def __init__(self, ident = 0 direction = CLIENT_TO_SERVER, data = {}):
		self.ident = ident
		self.direction = direction
		self.data = data

	def clone(self):
		return Packet(self.ident, self.direction, self.data)

	def decode(self, buff):
		self.ident = DecodeData(buff 'ubyte')[0]
		self.data = DecodePacket(buff)

	
	def encode(self):
		return EncodePacket(self.ident, self.data)

	def __repr__(self):
		if self.direction == TO_SERVER: s = ">>>"
		else: s = "<<<"
		format = "[%s] %s 0x%02x: %-"+str(max([len(i) for i in names.values()])+1)+"s%s"
		return format % (strftime("%H:%M:%S", gmtime()), s, self.ident, names[self.ident], str(self.data))

def read_packet(bbuff, direction):
	p = Packet(direction=direction)
	p.decode(bbuff)
	return p