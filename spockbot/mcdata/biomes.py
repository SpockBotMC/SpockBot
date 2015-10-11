import sys

from collections import namedtuple

from minecraft_data.v1_8 import biomes_list

from spockbot.mcdata.utils import camel_case, find_by, snake_case

biomes = {}
biomes_name = {}


def get_biome(biome):
    if isinstance(biome, int):  # by id
        return find_by(biome, biomes)
    else:  # by name
        return find_by(biome, biomes_name)


def _make_biome(biome_dict):
    name = biome_dict['name'].replace("+", " Plus")  # Extreme Hills+
    nt_name = '%sBiome' % camel_case(str(name))
    # Convert dict to a namedtuple
    nt = namedtuple(nt_name, biome_dict.keys())(**biome_dict)
    assert not hasattr(sys.modules[__name__], nt_name), \
        'Biome "%s" already registered at %s' % (nt_name, __name__)
    setattr(sys.modules[__name__], nt_name, nt)
    return nt


def _create_biomes():
    for biome in biomes_list:
        nt = _make_biome(biome)
        biomes[nt.id] = nt
        biomes_name[snake_case(nt.name)] = nt

_create_biomes()
