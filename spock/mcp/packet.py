from time import gmtime, strftime
from bound_buffer import BoundBuffer
import mcdata
import datautils
#from utils import ByteToHex

class Packet:
	def __init__(self, ident = 0, direction = mcdata.CLIENT_TO_SERVER, data = {}):
		self.ident = ident
		self.direction = direction
		self.data = data

	def clone(self):
		return Packet(self.ident, self.direction, self.data)

	def decode(self, buff):
		self.ident = datautils.DecodeData(buff, 'ubyte')
		self.data = {}
		if self.ident in mcdata.structs:
			for field in mcdata.structs[self.ident][self.direction]:
				if field[0] in mcdata.data_types or field[0] == 'string':
					data = datautils.DecodeData(buff, field[0])
				elif field[0] == 'byte_array' or field[0] == 'nbt':
					#Cheap shortcut used to get byte_array length, will almost certainly break in the future, fix this
					data = datautils.DecodeData(buff, field[0], length = self.data[field[1]+'_length'])
				self.data[field[1]] = data
		else:
			print "Something fucked up decoding packets"

	
	def encode(self):
		if self.ident in mcdata.structs:
			out = datautils.EncodeData(self.ident, 'ubyte')
			for field in mcdata.structs[self.ident][self.direction]:
				out += datautils.EncodeData(self.data[field[1]], field[0])
			return out
		else:
			print "Something fucked up encoding packets"

	def __repr__(self):
		if self.direction == mcdata.CLIENT_TO_SERVER: s = ">>>"
		else: s = "<<<"
		format = "[%s] %s 0x%02x: %-"+str(max([len(i) for i in mcdata.names.values()])+1)+"s%s"
		return format % (strftime("%H:%M:%S", gmtime()), s, self.ident, mcdata.names[self.ident], str(self.data))

def read_packet(bbuff, direction = mcdata.SERVER_TO_CLIENT):
	p = Packet(direction = direction)
	p.decode(bbuff)
	return p

def read_bytes(data, direction = mcdata.SERVER_TO_CLIENT):
	return read_packet(BoundBuffer(data), direction)