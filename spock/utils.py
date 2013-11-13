#Lacking a better place to put this, bbuff can live here for now
class BufferUnderflowException(Exception):
	pass

class BoundBuffer:
	backup = b''
	def __init__(self, *args):
		self.buff = (args[0] if args else b'')
	
	def recv(self, bytes):
		if len(self.buff) < bytes:
			raise BufferUnderflowException()
		o, self.buff = self.buff[:bytes], self.buff[bytes:]
		return o

	def append(self, bytes):
		self.buff += bytes
	
	def flush(self):
		out = self.buff
		self.buff = b''
		self.save()
		return out
	
	def save(self):
		self.backup = self.buff
	
	def revert(self):
		self.buff = self.backup

	def __len__(self):
		return self.buff.__len__()
	
	read = recv
	write = append

def ByteToHex( byteStr ):
	return ''.join( [ "%02X " % x for x in byteStr ] ).strip()

#TODO: Support 1.6 Server List Ping
def EncodeSLP(packet):
	pass

def DecodeSLP(packet):
	rstring = packet.data['reason'][3:].split('\x00')
	return {'protocol_version': int(rstring[0]),
		'server_version': rstring[1],
		'motd': rstring[2],
		'players': int(rstring[3]),
		'max_players': int(rstring[4]),
	}