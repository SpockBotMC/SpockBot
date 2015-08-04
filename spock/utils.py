"""
ALL THE UTILS!
"""
#silly python2
import copy
import math
from spock.vector import Vector3
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

class Position(Info):
    "Used for things that require encoding position for the protocol, use spock.vector.Vector3 if you want higher level vector functions"
    def __init__(self, x=0.0, y=0.0, z=0.0, vec=None):
        if vec:
            self.x, self.y, self.z = vec[:3]
        else:
            self.x = x
            self.y = y
            self.z = z

    def __str__(self):
        return "({:.2f}, {:.2f}, {:.2f})".format(self.x, self.y, self.z)

    def vec3(self):
        """
        Return a Vector3 object from this one
        """
        return Vector3(self.x, self.y, self.z)

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

def get_settings(defaults, settings):
    return dict(copy.deepcopy(defaults), **settings)

def mapshort2id(data):
    return data>>4, data&0x0F

def ByteToHex(byteStr):
    return ''.join( [ "%02X " % x for x in byteStr ] ).strip()
