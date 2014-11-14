#Lacking a better place to put this, bbuff can live here for now
class BufferUnderflowException(Exception):
	pass

class BoundBuffer:
	backup = b''
	def __init__(self, *args):
		self.count = 0
		self.buff = (args[0] if args else b'')

	def recv(self, bytes):
		if len(self.buff) < bytes:
			raise BufferUnderflowException()
		self.count += bytes
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

	def tell(self):
		return self.count

	def __len__(self):
		return self.buff.__len__()

	def __repr__(self):
		return 'BoundBuffer: ' + str(self.buff)

	read = recv
	write = append

def pl_announce(*args):
	def inner(cl):
		cl.pl_announce = args
		return cl
	return inner

def ByteToHex(byteStr):
	return ''.join( [ "%02X " % x for x in byteStr ] ).strip()
