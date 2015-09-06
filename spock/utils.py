"""
ALL THE UTILS!
"""
# silly python2
import copy
import re

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
        d = w if d is None else d
        super(BoundingBox, self).__init__(w, h, d)
        self.w = self.x
        self.h = self.y
        self.d = self.z


class BufferUnderflowException(Exception):
    pass


class BoundBuffer(object):
    buff = b''
    cursor = 0

    def __init__(self, data=b""):
        self.write(data)

    def read(self, length):
        if length > len(self):
            raise BufferUnderflowException()

        out = self.buff[self.cursor:self.cursor+length]
        self.cursor += length
        return out

    def write(self, data):
        self.buff += data

    def flush(self):
        return self.read(len(self))

    def save(self):
        self.buff = self.buff[self.cursor:]
        self.cursor = 0

    def revert(self):
        self.cursor = 0

    def tell(self):
        return self.cursor

    def __len__(self):
        return len(self.buff) - self.cursor

    def __repr__(self):
        return "<BoundBuffer '%s'>" % repr(self.buff[self.cursor:])

    recv = read
    append = write


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


# from http://stackoverflow.com/a/12867228
re_spaced_caps = re.compile(r'((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')


def split_words(text):  # TODO lacking a better name
    if '_' in text:
        return [w.lower() for w in text.split('_')]
    if ' ' not in text:
        text = re_spaced_caps.sub(r' \1', text)
    return [w.lower() for w in text.split(' ')]


def snake_case(text):
    return '_'.join(split_words(text))


def camel_case(text):
    return ''.join(map(str.capitalize, split_words(text)))
