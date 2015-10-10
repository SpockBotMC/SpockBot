import sys

from minecraft_data.v1_8 import biomes_list

from spockbot.mcdata.utils import camel_case, find_by, snake_case

biomes = {}
biomes_name = {}


def get_biome(biome):
    if isinstance(biome, int):  # by id
        return find_by(biome, biomes)
    else:  # by name
        return find_by(biome, biomes_name)


class Biome(object):
    id = -1
    color = 0
    name = 'Biome'
    rainfall = 0.3
    temperature = 0.0


def _make_biome(biome_dict):
    biome_dict = biome_dict.copy()
    cls_name = '%sBiome' % camel_case(str(biome_dict['name']))
    bases = (Biome,)
    attrs = biome_dict.copy()
    attrs['__module__'] = sys.modules[__name__]

    cls = type(cls_name, bases, attrs)
    assert not hasattr(sys.modules[__name__], cls_name), \
        'Biome "%s" already registered at %s' % (cls_name, __name__)
    setattr(sys.modules[__name__], cls_name, cls)
    return cls


def _create_biomes():
    for biome in biomes_list:
        cls = _make_biome(biome)
        biomes[cls.id] = cls
        biomes_name[snake_case(cls.name)] = cls

_create_biomes()
