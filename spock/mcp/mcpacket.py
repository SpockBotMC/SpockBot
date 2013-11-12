import copy
from time import gmtime, strftime
from spock import utils
from spock.mcp import datautils, mcdata
from spock.mcp.mcpacket_extensions import hashed_extensions

#TODO: Wow this class ended up a bit of a mess, cleanup and refactor soon^TM
class Packet(object):
	def __init__(self,
		ident = [mcdata.HANDSHAKE_STATE, mcdata.CLIENT_TO_SERVER, 0x00],
		data = {}
	):
		self.__ident = list(ident)
		#Quick hack to fake default ident
		if len(self.__ident) == 2:
			self.__ident.append(0x00)
		self.__hashed_ident = tuple(self.__ident)
		self.data = data

	def clone(self):
		return Packet(self.__ident, copy.deepcopy(self.data))

	def ident(self, new_ident = None):
		if new_ident:
			self.__ident = list(new_ident)
			self.__hashed_ident = tuple(new_ident)
		return self.__hashed_ident

	def decode(self, bbuff):
		pbuff = utils.BoundBuffer(bbuff.recv(datautils.unpack('varint', bbuff)))
		#Ident
		self.__ident[2] = datautils.unpack(pbuff, 'ubyte')
		self.__hashed_ident = tuple(self.__ident)
		#Payload
		for dtype, name in mcdata.hashed_structs[self.__hashed_ident]:
			self.data[name] = datautils.unpack(dtype, pbuff)
		#Extension
		if self.__ident in hashed_extensions:
			hashed_extensions[self.__hashed_ident].decode_extra(self, pbuff)
		return self
	
	def encode(self):
		#Ident
		o = datautils.pack('ubyte', self.__ident[2])
		#Payload
		for dtype, name in mcdata.hashed_structs[self.__hashed_ident]:
			o += datautils.pack(dtype, self.data[name])
		#Extension
		if self.__ident in hashed_extensions:
			o += hashed_extensions[self.__hashed_ident].encode_extra(self)
		return datautils.pack('varint', len(o)) + o

	def __repr__(self):
		if self.__ident[1] == mcdata.CLIENT_TO_SERVER: s = ">>>"
		else: s = "<<<"
		format = "[%s] %s (0x%02X, 0x%02X): %-"+str(max([len(i) for i in mcdata.hashed_names.values()])+1)+"s%s"
		return format % (strftime("%H:%M:%S", gmtime()), s, self.__ident[0], self.__ident[2], mcdata.hashed_names[self.__hashed_ident], str(self.data))