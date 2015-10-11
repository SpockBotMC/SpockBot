import sys
from collections import defaultdict, namedtuple

from minecraft_data.v1_8 import materials as materials_by_name

from spockbot.mcdata.utils import camel_case, find_by

materials = {}


def get_material(name):
    return find_by(name, materials)


def _make_material(name, material_dict):
    eff = {int(k): float(v) for k, v in material_dict.items()}
    eff = defaultdict(lambda: 1.0, eff)
    nt_name = '%sMaterial' % camel_case(str(name))
    # Convert dict to a namedtuple
    nt_class = namedtuple(nt_name, ['name', 'tool_effectiveness'])
    nt = nt_class(name=name, tool_effectiveness=eff)
    assert not hasattr(sys.modules[__name__], nt_name), \
        'Material "%s" already registered at %s' % (nt_name, __name__)
    setattr(sys.modules[__name__], nt_name, nt)
    return nt


def _create_materials():
    for name, data in materials_by_name.items():
        nt = _make_material(name, data)
        materials[nt.name] = nt

_create_materials()
