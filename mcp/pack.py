import struct
import collections
from StringIO import StringIO
import gzip

endian = '!'

def unpack(buff, format):
	return struct.unpack_from(endian+format, buff.read(struct.calcsize(format)))[0]
def pack(value, format):
	return struct.pack(endian+format, value)

class t_Base():
	def __init__(self, ty, *args):
		self.type = ty
		if args:
			self.name = args[0]
		else: self.name = ''
	def __getattr__(self, name):
		return getattr(self.value, name)
	def __getitem__(self, name):
		return self.value[name]
	def decode(self, buff):
		self.value = unpack(buff, self.struct)
	def encode(self):
		return pack(self.value, self.struct)
	def normalized(self):
		return self.value

class t_Bool(t_Base):
	struct = '?'
class t_uByte(t_Base):
	struct = 'B'
class t_Byte(t_Base):
	struct = 'b'
class t_uShort(t_Base):
	struct = 'H'
class t_Short(t_Base):
	struct = 'h'
class t_uInt(t_Base):
	struct = 'I'
class t_Int(t_Base):
	struct = 'i'
class t_Long(t_Base):
	struct = 'q'
class t_Float(t_Base):
	struct = 'f'
class t_Double(t_Base):
	struct = 'd'

class t_Byte_Array(t_Base):
	def decode(self, buff):
		l = unpack(buff, 'i')
		self.value = [unpack(buff, 'b') for i in range(l)]
	def encode(self):
		o = pack(len(self.value), 'i')
		o += ''.join([pack(i, 'b') for i in self.value])
		return o

class t_String(t_Base):
	def decode(self, buff):
		l = unpack(buff, 'h')
		self.value = buff.read(l)
	def encode(self):
		return pack(len(self.value), 'h') + self.value

class t_List(t_Base):
	def decode(self, buff):
		self.child_t_Base = unpack(buff, 'b')
		l = unpack(buff, 'i')
		self.value = []
		for i in range(l):
			child = handlers[self.child_t_Base](self.child_t_Base)
			child.decode(buff)
			self.value.append(child)
	def encode(self):
		o = pack(self.child_t_Base, 'b')
		o+= pack(len(self.value), 'i')
		o+= ''.join([i.encode() for i in self.value])
		return o
	def normalized(self):
		return [i.normalized() for i in self.value]

class t_Compound(t_Base):
	def decode(self, buff):
		self.value = collections.OrderedDict()
		child_t_Base = buff.read(1)
		while child_t_Base != '' and child_t_Base != '\x00':
			child_t_Base = ord(child_t_Base)
			name_len = unpack(buff, 'h')
			name = buff.read(name_len)
			child = handlers[child_t_Base](child_t_Base, name)
			child.decode(buff)
			self.value[name] = child
			child_t_Base = buff.read(1)
	def encode(self):
		o = ''
		for name, child in self.value.items():
			o += pack(child.type, 'b') #Type
			o += pack(len(name), 'h')  #Name length
			o += name				  #Name
			o += child.encode()		#Payload
		return o + '\x00'
	def normalized(self):
		return dict([(name, child.normalized()) for name, child in self.value.items()])

handlers = {
	1: t_Byte,
	2: t_Short,
	3: t_Int,
	4: t_Long,
	5: t_Float,
	6: t_Double,
	7: t_Byte_Array,
	8: t_String,
	9: t_List,
	10: t_Compound,
	}

def decode(buff):
	t = t_Compound(10)
	t.decode(buff)
	return list(t.value.values())[0]

def encode(obj):
	t = t_Compound(10)
	t.value = {'': obj}
	return t.encode()[:-1]

def compress(s):
	io = StringIO()
	f = gzip.GzipFile(fileobj=io, mode='w')
	f.write(s)
	f.close()
	return io.getvalue()

def decompress(s):
	f = gzip.GzipFile(fileobj=StringIO(s))
	o = f.read()
	f.close()
	return o
