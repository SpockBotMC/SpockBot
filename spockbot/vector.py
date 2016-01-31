from __future__ import division

import math


class BaseVector(object):
    _internal_vec_type = list

    def __init__(self, *values):
        self.vector = self._internal_vec_type(values)

    def init(self, *args):
        BaseVector.__init__(self, *args)
        return self

    def __iter__(self):
        return self.vector.__iter__()

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__,
                           ', '.join(map(str, self.vector)))

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

    def __iadd__(self, other):
        self.vector = list(map(sum, zip(self, other)))
        return self

    iadd = __iadd__

    def __neg__(self):
        return self.__class__(*map(lambda a: -a, self))

    def __sub__(self, other):
        return self.__class__(*map(lambda a: a[0] - a[1], zip(self, other)))

    def __isub__(self, other):
        self.vector = list(map(lambda a: a[0] - a[1], zip(self, other)))
        return self

    isub = __isub__

    def __mul__(self, other):
        return self.__class__(*map(lambda a: a * other, self))

    def __imul__(self, other):
        self.vector = list(map(lambda a: a * other, self))
        return self

    imul = __imul__
    __rmul__ = __mul__

    def __truediv__(self, other):
        return self.__class__(*map(lambda a: a / other, self))

    def __itruediv__(self, other):
        self.vector = list(map(lambda a: a / other, self))
        return self

    itruediv = __itruediv__
    __div__ = __truediv__
    __idiv__ = __itruediv__
    idiv = __idiv__

    # More advanced math

    def trunc(self):
        return math.trunc(self)

    def __trunc__(self):
        return self.__class__(*map(math.trunc, self))

    # Utilities

    def zero(self):
        self.vector = [0 for a in self]

    def iceil(self):
        self.vector = [int(math.ceil(a)) for a in self]
        return self

    def ifloor(self):
        self.vector = [int(math.floor(a)) for a in self]
        return self

    def ceil(self):
        return self.__class__(*self).iceil()

    def floor(self):
        return self.__class__(*self).ifloor()

    def dot_product(self, other):
        return sum(map(lambda a: a[0] * a[1], zip(self, other)))

    def dist_cubic(self, other=None):
        """ Manhattan distance """
        v = self - other if other else self
        return sum(map(abs, v.vector))

    def dist_sq(self, other=None):
        """ For fast length comparison """
        v = self - other if other else self
        return sum(map(lambda a: a * a, v))

    def dist(self, other=None):
        return math.sqrt(self.dist_sq(other))

    def norm(self):
        return self / self.dist()

    # Truthy evaluation
    def __bool__(self):
        return any(self)
    __nonzero__ = __bool__

    # Comparisons

    def __hash__(self):
        return hash(tuple(self.vector))

    def __lt__(self, other):
        return self.dist_sq() < other.dist_sq()

    def __gt__(self, other):
        return self.dist_sq() > other.dist_sq()

    def __le__(self, other):
        return not self.__gt__(other)

    def __ge__(self, other):
        return not self.__lt__(other)

    def __eq__(self, other):
        return all(s == o for s, o in zip(self, other))


class Vector3(CartesianVector):
    def __init__(self, *xyz):
        l = len(xyz)
        if l == 1:
            obj = xyz[0]
            try:
                xyz = obj.x, obj.y, obj.z
            except AttributeError:
                try:
                    xyz = obj['x'], obj['y'], obj['z']
                except TypeError:
                    xyz = tuple(obj[:3])
        elif l == 0:
            xyz = (0, 0, 0)
        elif l != 3:
            raise ValueError('Wrong length: expected 3, got %s' % xyz)
        super(Vector3, self).__init__(*xyz)

    def init(self, *args):
        Vector3.__init__(self, *args)
        return self

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

    @property
    def yaw_pitch(self):
        """
        Calculate the yaw and pitch of this vector
        """
        if not self:
            return YawPitch(0, 0)
        ground_distance = math.sqrt(self.x ** 2 + self.z ** 2)
        if ground_distance:
            alpha1 = -math.asin(self.x / ground_distance) / math.pi * 180
            alpha2 = math.acos(self.z / ground_distance) / math.pi * 180
            if alpha2 > 90:
                yaw = 180 - alpha1
            else:
                yaw = alpha1
            pitch = math.atan2(-self.y, ground_distance) / math.pi * 180
        else:
            yaw = 0
            y = round(self.y)
            if y > 0:
                pitch = -90
            elif y < 0:
                pitch = 90
            else:
                pitch = 0
        return YawPitch(yaw, pitch)

    def set_dict(self, data):
        self.vector[0] = data['x']
        self.vector[1] = data['y']
        self.vector[2] = data['z']

    def get_dict(self):
        return {'x': self.vector[0], 'y': self.vector[1], 'z': self.vector[2]}


class YawPitch(BaseVector):
    """
    Store the yaw and pitch (in degrees)
    """

    def __init__(self, *args):
        assert len(args) == 2, 'Wrong length: expected 2, got %s' % args
        super(YawPitch, self).__init__(*args)

    def init(self, *args):
        YawPitch.__init__(self, *args)
        return self

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
        return self.vector[0] / 180 * math.pi

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
        return self.vector[1] / 180 * math.pi

    def unit_vector(self):
        """Generate a unit vector (norm = 1)"""
        x = -math.cos(self.rpitch) * math.sin(self.ryaw)
        y = -math.sin(self.rpitch)
        z = math.cos(self.rpitch) * math.cos(self.ryaw)
        return Vector3(x, y, z)
