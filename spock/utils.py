"""
ALL THE UTILS!
"""
# silly python2
import copy

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
        return repr(self.get_dict()).replace('dict', self.__class__.__name__)

    def __str__(self):
        return str(self.get_dict())


class Position(Vector3, Info):
    """
    Used for things that require encoding position for the protocol,
    but also require higher level vector functions.
    """

    def get_dict(self):
        d = self.__dict__.copy()
        del d['vector']
        d['x'], d['y'], d['z'] = self
        return d


class BoundingBox(Vector3):
    def __init__(self, w, h, d=None):
        d = w if d == None else d
        super(BoundingBox, self).__init__(w, h, d)
        self.w = self.x
        self.h = self.y
        self.d = self.z

class BufferUnderflowException(Exception):
    pass


class BoundBuffer(object):
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
    return data >> 4, data & 0x0F


def byte_to_hex(byte_str):
    return ''.join(["%02X " % x for x in byte_str]).strip()
