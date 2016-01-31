from collections import defaultdict, namedtuple

from minecraft_data.v1_8 import recipes as raw_recipes


RecipeItem = namedtuple('RecipeItem', 'id meta amount')


class Recipe(object):
    def __init__(self, raw):
        self.result = reformat_item(raw['result'], None)
        if 'ingredients' in raw:
            self.ingredients = [reformat_item(item, 0)
                                for item in raw['ingredients']]
            self.in_shape = None
            self.out_shape = None
        else:
            self.in_shape = reformat_shape(raw['inShape'])
            self.out_shape = reformat_shape(raw['outShape']) \
                if 'outShape' in raw else None
            self.ingredients = [item for row in self.in_shape for item in row]

    @property
    def total_ingredient_amounts(self):
        """
        Returns:
            dict: In the form { (item_id, metadata) -> amount }
        """
        totals = defaultdict(int)
        for id, meta, amount in self.ingredients:
            totals[(id, meta)] += amount
        return totals

    @property
    def ingredient_positions(self):
        """
        Returns:
            dict: In the form { (item_id, metadata) -> [(x, y, amount), ...] }
        """
        positions = defaultdict(list)
        for y, row in enumerate(self.in_shape):
            for x, (item_id, metadata, amount) in enumerate(row):
                positions[(item_id, metadata)].append((x, y, amount))
        return positions


def reformat_item(raw, default_meta=None):
    if isinstance(raw, dict):
        raw = raw.copy()  # do not modify arg
        if 'metadata' not in raw:
            raw['metadata'] = default_meta
        if 'count' not in raw:
            raw['count'] = 1
        return RecipeItem(raw['id'], raw['metadata'], raw['count'])
    elif isinstance(raw, list):
        return RecipeItem(raw[0], raw[1], 1)
    else:  # single ID or None
        return RecipeItem(raw or None, default_meta, 1)


def reformat_shape(shape):
    return [[reformat_item(item, None) for item in row] for row in shape]


def iter_recipes(item_id, meta=None):
    item_id = str(item_id)
    meta = meta and int(meta)
    try:
        recipes_for_item = raw_recipes[item_id]
    except KeyError:
        return  # no recipe found, do not yield anything
    else:
        for raw in recipes_for_item:
            recipe = Recipe(raw)
            if meta is None or meta == recipe.result.meta:
                yield recipe


def get_any_recipe(item, meta=None):
    # TODO return small recipes if present
    for matching in iter_recipes(item, meta):
        return matching
    return None
