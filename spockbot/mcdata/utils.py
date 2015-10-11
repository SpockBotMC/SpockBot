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


def find_by(key, *args):
    for arg in args:
        if key in arg:
            return arg[key]
    return None


# from http://stackoverflow.com/a/12867228
re_spaced_caps = re.compile(r'((?<=[a-z0-9])[A-Z]|(?!^)[A-Z](?=[a-z]))')

# from  http://stackoverflow.com/a/3303361
# Remove invalid characters
re_invalid_var = re.compile(r'[^0-9a-zA-Z_]')

# Remove leading characters until we find a letter or underscore
re_invalid_start = re.compile(r'^[^a-zA-Z_]+')


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


def clean_var(text):
    """Turn text into a valid python classname or variable"""
    text = re_invalid_var.sub('', text)
    text = re_invalid_start.sub('', text)
    return text
