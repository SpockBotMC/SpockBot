"""
Craft items.
"""
from math import ceil

from spockbot.mcdata.recipes import get_any_recipe
from spockbot.plugins.base import PluginBase, pl_announce
from spockbot.plugins.tools.task import TaskFailed


@pl_announce('Craft')
class CraftPlugin(PluginBase):
    requires = ('Inventory', 'TaskManager')

    def __init__(self, ploader, settings):
        super(CraftPlugin, self).__init__(ploader, settings)
        ploader.provides('Craft', self)

    def craft(self, item=None, meta=None, amount=1, recipe=None, parent=None):
        """
        Starts a ``craft_task``. Either ``item`` or ``recipe`` has to be given.

        Returns:
            Optional[Recipe]: The recipe used for crafting.
        """
        if recipe:
            item, meta, _ = recipe.result
        else:
            recipe = get_any_recipe(item, meta)
        if recipe:
            self.taskmanager.run_task(self.craft_task(recipe, amount), parent)
        return recipe

    def craft_task(self, recipe, amount=1):
        """
        A task that crafts ``amount`` items with ``recipe``.
        """
        if not recipe:
            raise TaskFailed('[Craft] No recipe given: %s' % recipe)
        if amount <= 0:
            raise TaskFailed('[Craft] Nothing to craft, amount=%s' % amount)

        inv = self.inventory
        craft_times = int(ceil(amount / recipe.result.amount))

        try:  # check if open window supports crafting
            grid_slots = inv.window.craft_grid_slots
            result_slot = inv.window.craft_result_slot
        except AttributeError:
            raise TaskFailed('[Craft] %s is no crafting window'
                             % inv.window.__class__.__name__)

        num_grid_slots = len(grid_slots)
        try:
            grid_width = {4: 2, 9: 3}[num_grid_slots]
        except KeyError:
            raise TaskFailed('Crafting grid has unsupported size of'
                             ' %i instead of 4 or 9' % num_grid_slots)

        grid_height = num_grid_slots / grid_width
        row1 = recipe.in_shape[0]
        if len(recipe.in_shape) > grid_height or len(row1) > grid_width:
            raise TaskFailed('Recipe for %s does not fit in a %ix%i grid'
                             % (recipe.result, grid_width, grid_height))

        storage_slots = inv.window.persistent_slots

        # check ingredients for recipe
        total_amounts_needed = recipe.total_ingredient_amounts
        for ingredient, needed in total_amounts_needed.items():
            needed *= craft_times
            stored = inv.total_stored(ingredient, storage_slots)
            if needed > stored:
                raise TaskFailed('Missing %s not stored, have %s of %i'
                                 % ('%s:%s' % ingredient, stored, needed))

        # put ingredients into crafting grid
        for ingredient, p in recipe.ingredient_positions.items():
            for (x, y, ingredient_amount) in p:
                slot = grid_slots[x + y * grid_width]
                for i in range(ingredient_amount * craft_times):
                    if inv.cursor_slot.is_empty:
                        ingr_slot = inv.find_slot(ingredient, storage_slots)
                        if not ingr_slot:  # should not occur, as we checked
                            raise TaskFailed('Craft: No %s:%s found'
                                             ' in inventory' % ingredient)
                        yield inv.async.click_slot(ingr_slot)
                    # TODO speed up mass crafting with left+right clicking
                    yield inv.async.click_slot(slot, right=True)
            # done putting in that item, put away
            if not inv.cursor_slot.is_empty:
                yield inv.async.store_or_drop()

        # TODO check if all items are in place
        # otherwise we will get the wrong crafting result

        # take crafted items
        prev_cursor_amt = inv.cursor_slot.amount
        crafted_amt = 0
        while amount > crafted_amt + inv.cursor_slot.amount:
            yield inv.async.click_slot(result_slot)
            # TODO check that cursor is non-empty, otherwise we did not craft
            result_stack_size = inv.cursor_slot.item.stack_size
            if inv.cursor_slot.amount in (prev_cursor_amt, result_stack_size):
                # cursor full, put away
                crafted_amt += inv.cursor_slot.amount
                yield inv.async.store_or_drop()
            prev_cursor_amt = inv.cursor_slot.amount
        if not inv.cursor_slot.is_empty:
            # cursor still has items left from crafting, put away
            yield inv.async.store_or_drop()

        # put ingredients left from crafting back into inventory
        yield inv.async.move_to_inventory(grid_slots)

        # TODO return anything? maybe the slots with the crafting results?
