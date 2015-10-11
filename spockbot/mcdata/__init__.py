from spockbot.mcdata import blocks
from spockbot.mcdata import items
from spockbot.mcdata.utils import find_by


def get_item_or_block(find):
    if isinstance(find, int):  # by id
        return find_by(find, items.items, blocks.blocks)
    else:  # by name
        return find_by(find, items.items_name, blocks.blocks_name)
