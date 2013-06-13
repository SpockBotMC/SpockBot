from time import gmtime, strftime
from spock import bound_buffer
import mcpacket_extensions
import mcdata
import datautils
#from utils import ByteToHex

class Packet(object):
	def __init__(self, ident = 0, direction = mcdata.CLIENT_TO_SERVER, data = {}):
		self.ident = ident
		self.direction = direction
		self.data = data

	def clone(self):
		return Packet(self.ident, self.direction, self.data)

	def decode(self, bbuff):
		#Ident
		self.ident = datautils.unpack(bbuff, 'ubyte')
		
		#print hex(self.ident)
		
		#Payload
		for dtype, name in mcdata.structs[self.ident][self.direction]:
			self.data[name] = datautils.unpack(bbuff, dtype)
		
		#Extension
		if self.ident in mcpacket_extensions.extensions:
			mcpacket_extensions.extensions[self.ident].decode_extra(self, bbuff)
	
	def encode(self):
		#Ident
		output = datautils.pack('ubyte', self.ident)
		
		#Extension
		if self.ident in mcpacket_extensions.extensions:
			append = mcpacket_extensions.extensions[self.ident].encode_extra(self)
		else:
			append = ''
		
		#Payload
		for dtype, name in mcdata.structs[self.ident][self.direction]:
			output += datautils.pack(dtype, self.data[name])

		return output + append

	def __repr__(self):
		if self.direction == mcdata.CLIENT_TO_SERVER: s = ">>>"
		else: s = "<<<"
		format = "[%s] %s 0x%02X: %-"+str(max([len(i) for i in mcdata.names.values()])+1)+"s%s"
		return format % (strftime("%H:%M:%S", gmtime()), s, self.ident, mcdata.names[self.ident], str(self.data))

def read_packet(bbuff, direction = mcdata.SERVER_TO_CLIENT):
	p = Packet(direction = direction, data = {})
	p.decode(bbuff)
	return p

def decode_packet(data, direction = mcdata.SERVER_TO_CLIENT):
	return read_packet(bound_buffer.BoundBuffer(data), direction)