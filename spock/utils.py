"""
ALL THE UTILS!
"""
#silly python2
import copy
try:
	string_types = unicode
except NameError:
	string_types = str

class Vec3:
	def __init__(self, x, y, z):
		self.x = x
		self.y = y
		self.z = z

	def add_vector(self, x = None, y = None, z = None, vec = None):
		if vec:
			self.x += vec.x
			self.y += vec.y
			self.z += vec.z
		else:
			if x: self.x += x
			if y: self.y += y
			if z: self.z += z

	def __str__(self):
		return "({:.2f}, {:.2f}, {:.2f})".format(self.x, self.y, self.z)

class BoundingBox:
	def __init__(self, w, h, d=None, offset=(0,0,0)):
		self.x = offset[0]
		self.y = offset[1]
		self.z = offset[2]
		self.w = w #x
		self.h = h #y
		if d:
			self.d = d #z
		else:
			self.d = w

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

def get_settings(settings, defaults):
	final_settings = copy.deepcopy(defaults)
	for k, v in settings.items():
		final_settings[k] = v
	return final_settings

def mapshort2id(data):
	return data>>4, data&0x0F

def ByteToHex(byteStr):
	return ''.join( [ "%02X " % x for x in byteStr ] ).strip()
