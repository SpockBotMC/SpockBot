"""
ALL THE UTILS!
"""
#silly python2
import copy
import math
try:
	string_types = unicode
except NameError:
	string_types = str

class Info(object):
	def set_dict(self, data):
		for key in data:
			if hasattr(self, key):
				setattr(self, key, data[key])

	def get_dict(self):
		return self.__dict__

	def __repr__(self):
		return repr(self.__dict__)

	def __str__(self):
		return str(self.__dict__)

class Vec3(Info):
	def __init__(self, x=0.0, y=0.0, z=0.0, vec=None):
		if vec:
			self.x, self.y, self.z = vec[:3]
		else:
			self.x = x
			self.y = y
			self.z = z

	def add_vector(self, x=None, y=None, z=None, vec=None):
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

	def to_Vector3(self):
		"""
		Return a Vector3 object from this one
		"""
		return Vector3(self.x, self.y, self.z)


class BaseVector(object):
	_internal_vec_type = list
	def __init__(self, *values):
		self.vector = self._internal_vec_type(values)

	def __iter__(self):
		return self.vector.__iter__()

	def __repr__(self):
		return "%s(" % self.__class__.__name__ + ", ".join(map(str, self.vector)) + ")"

	__str__ = __repr__

	def __setitem__(self, key, value):
		self.vector[key] = value

	def __getitem__(self, item):
		return self.vector[item]

	def __len__(self):
		return len(self.vector)


class CartesianVector(BaseVector):

	# Math operations
	# Is __abs__ really useful ?
	def __abs__(self):
		return self.__class__(*map(abs, self.vector))

	def __add__(self, other):
		return self.__class__(*map(sum, zip(self, other)))

	__iadd__ = __add__

	def __neg__(self):
		return self.__class__(*map(lambda a:-a, self))

	def __sub__(self, other):
		return self.__class__(*map(lambda a:a[0] - a[1], zip(self, other)))

	__isub__ = __sub__

	def __mul__(self, other):
		return self.__class__(*map(lambda a:a * other, self))

	__imul__ = __mul__
	__rmul__ = __mul__

	def __truediv__(self, other):
		return self.__class__(*map(lambda a:a / other, self))

	__itruediv__ = __truediv__

	# More advanced math

	def trunc(self):
		return math.trunc(self)

	def __trunc__(self):
		return self.__class__(*map(math.trunc, self))

	def norm(self):
		return math.sqrt(sum(map(lambda a:a*a, self)))

	# Comparisons
	# XXX : Maybe return another type of Vector
	def __le__(self, other):
		return self.__class__(*map(lambda a: a[0] <= a[1], zip(self, other)))

	def __lt__(self, other):
		return self.__class__(*map(lambda a: a[0] < a[1], zip(self, other)))

	def __ge__(self, other):
		return self.__class__(*map(lambda a: a[0] >= a[1], zip(self, other)))

	def __gt__(self, other):
		return self.__class__(*map(lambda a: a[0] > a[1], zip(self, other)))

	def __eq__(self, other):
		return self.__class__(*map(lambda a: a[0] > a[1], zip(self, other)))

# correspond to Vec3
class Vector3(CartesianVector):
	def __init__(self, *args):
		assert len(args)==3, "Wrong length"
		super(Vector3, self).__init__(*args)

	# Some shortcuts
	@property
	def x(self):
		return self.vector[0]

	@x.setter
	def x(self, value):
		self.vector[0] = value

	@property
	def y(self):
		return self.vector[1]

	@y.setter
	def y(self, value):
		self.vector[1] = value

	@property
	def z(self):
		return self.vector[2]

	@z.setter
	def z(self, value):
		self.vector[2] = value

	def yaw_pitch(self):
		"""
		Calculate the yaw and pitch of this vector
		"""
		try:
			c = math.sqrt( self.x**2 + self.z**2 )
			alpha1 = -math.asin(self.x/c)/math.pi*180
			alpha2 =  math.acos(self.z/c)/math.pi*180
			if alpha2 > 90:
				yaw = 180 - alpha1
			else:
				yaw = alpha1
			pitch = math.asin(-self.y/c)/math.pi*180
		except ZeroDivisionError:
			yaw = 0
			pitch = 0
		return YawPitch(yaw, pitch)

class YawPitch(BaseVector):
	"""
	Store the yaw and pitch (in degrees)
	"""
	def __init__(self, *args):
		assert len(args)==2, "Wrong length"
		super(YawPitch, self).__init__(*args)

	# Some shortcuts
	@property
	def yaw(self):
		"""Yaw in degrees"""
		return self.vector[0]

	@yaw.setter
	def yaw(self, value):
		self.vector[0] = value

	@property
	def ryaw(self):
		"""Yaw in radians"""
		return self.vector[0]/180*math.pi

	@property
	def pitch(self):
		"""Pitch in degrees"""
		return self.vector[1]

	@pitch.setter
	def pitch(self, value):
		self.vector[1] = value

	@property
	def rpitch(self):
		"""Pitch in radians"""
		return self.vector[1]/180*math.pi

	def unit_vector(self):
		"""Generate a unit vector (norm = 1)"""
		x = -math.cos(self.rpitch) * math.sin(self.ryaw)
		y = -math.sin(self.rpitch)
		z =  math.cos(self.rpitch) * math.cos(self.ryaw)
		return Vector3(x, y, z)

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

def pl_event(*args):
	def inner(cl):
		cl.pl_event = args
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
