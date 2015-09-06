from collections import defaultdict, namedtuple

from minecraft_data.v1_8 import recipes as raw_recipes


RecipeItem = namedtuple('RecipeItem', 'id meta amount')
Recipe = namedtuple('Recipe', 'result ingredients in_shape out_shape')


def to_recipe(raw):
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

    result = reformat_item(raw['result'], None)
    if 'ingredients' in raw:
        ingredients = [reformat_item(item, 0) for item in raw['ingredients']]
        in_shape = out_shape = None
    else:
        in_shape = reformat_shape(raw['inShape'])
        out_shape = reformat_shape(raw['outShape']) \
            if 'outShape' in raw else None
        ingredients = [item for row in in_shape for item in row]  # flatten
    return Recipe(result, ingredients, in_shape, out_shape)


def iter_recipes(item_id, meta=None):
    item_id = str(item_id)
    meta = meta and int(meta)
    try:
        recipes_for_item = raw_recipes[item_id]
    except KeyError:
        return  # no recipe found, do not yield anything
    else:
        for raw in recipes_for_item:
            recipe = to_recipe(raw)
            if meta is None or meta == recipe.result.meta:
                yield recipe


def find_recipe(item, meta=None):
    # TODO return small recipes if present
    for matching in iter_recipes(item, meta):
        return matching
    return None


def total_ingredient_amounts(recipe):
    totals = defaultdict(int)
    for id, meta, amount in recipe.ingredients:
        totals[(id, meta)] += amount
    return totals
