import re

from spockbot.vector import Vector3


class BoundingBox(Vector3):
    def __init__(self, w, h, d=None):
        d = w if d is None else d
        super(BoundingBox, self).__init__(w, h, d)
        self.w = self.x
        self.h = self.y
        self.d = self.z


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
