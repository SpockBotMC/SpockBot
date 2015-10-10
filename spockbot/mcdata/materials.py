import sys
from collections import defaultdict

from minecraft_data.v1_8 import materials as materials_by_name

from spockbot.mcdata.utils import camel_case, find_by

materials = {}


def get_material(name):
    return find_by(name, materials)


class Material(object):
    name = "material"
    speed = defaultdict(lambda: 1.0)


def _make_material(name, material_dict):
    material_dict = material_dict.copy()
    cls_name = '%sMaterial' % camel_case(str(name))
    bases = (Material,)
    speed = {int(k): float(v) for k, v in material_dict.items()}
    attrs = {
        '__module__': sys.modules[__name__],
        'name': name,
        'speed': defaultdict(lambda: 1.0, speed)
    }

    cls = type(cls_name, bases, attrs)
    assert not hasattr(sys.modules[__name__], cls_name), \
        'Material "%s" already registered at %s' % (cls_name, __name__)
    setattr(sys.modules[__name__], cls_name, cls)
    return cls


def _create_materials():
    for name, data in materials_by_name.items():
        cls = _make_material(name, data)
        materials[cls.name] = cls

_create_materials()
