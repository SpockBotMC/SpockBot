import math

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
        return self.__class__(*map(lambda a: a[0] == a[1], zip(self, other)))


class Vector3(CartesianVector):
    def __init__(self, *args):
        assert len(args)==3, "Wrong length"
        super(self.__class__, self).__init__(*args)

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

    def set_dict(self, data):
        if set(("x", "y", "z")) <= set(data):
            self.vector[0] = data['x']
            self.vector[1] = data['y']
            self.vector[2] = data['z']

    def get_dict(self):
        return {'x': self.vector[0],'y': self.vector[1],'z':self.vector[2]}

class YawPitch(BaseVector):
    """
    Store the yaw and pitch (in degrees)
    """
    def __init__(self, *args):
        assert len(args)==2, "Wrong length"
        super(self.__class__, self).__init__(*args)

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
