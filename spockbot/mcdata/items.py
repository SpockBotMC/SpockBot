import sys

from minecraft_data.v1_8 import items_list

from spockbot.mcdata.utils import camel_case, find_by

items = {}
items_name = {}


def get_item(item, meta=0, init=True):
    ret = None
    if isinstance(item, int):  # by id
        ret = find_by(item, items)
    else:  # by name
        ret = find_by(item, items_name)
    if init and ret is not None:
        return ret(meta)
    return ret


class Item(object):
    id = -1
    display_name = "Item"
    stack_size = 0
    name = "item"
    variations = {}

    def __init__(self, meta=None):
        if meta is None:
            return
        self.metadata = meta
        if self.metadata in self.variations:
            # TODO: apply other all possible variations
            self.display_name = self.variations[self.metadata]["display_name"]

    def __str__(self):
        return '%s %i:%i' % (self.display_name, self.id,
                             getattr(self, 'metadata', 0))


def _make_item(item_dict):
    cls_name = '%sItem' % camel_case(str(item_dict['name']))
    bases = (Item,)
    variations = {}
    if "variations" in item_dict:
        for var in item_dict['variations']:
            variations[var['metadata']] = {"display_name": var['displayName']}
    attrs = {
        '__module__': sys.modules[__name__],
        'id': item_dict['id'],
        'name': item_dict['name'],
        'display_name': item_dict['displayName'],
        'stack_size': item_dict['stackSize'],
        'variations': variations,
    }

    cls = type(cls_name, bases, attrs)
    assert not hasattr(sys.modules[__name__], cls_name), \
        'Item "%s" already registered at %s' % (cls_name, __name__)
    setattr(sys.modules[__name__], cls_name, cls)
    return cls


def _create_items():
    for item in items_list:
        cls = _make_item(item)
        items[cls.id] = cls
        items_name[cls.name] = cls

_create_items()
