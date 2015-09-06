"""
Look up recipes and craft items.
"""
from math import ceil

from spock.mcdata.recipes import find_recipe, total_ingredient_amounts
from spock.plugins.base import PluginBase
from spock.task import RunTask, TaskFailed
from spock.utils import pl_announce


@pl_announce('Craft')
class CraftPlugin(PluginBase):
    requires = ('Event', 'Inventory')

    def __init__(self, ploader, settings):
        super(CraftPlugin, self).__init__(ploader, settings)
        ploader.provides('Craft', self)

    def craft(self, item=None, meta=None, amount=1, recipe=None, parent=None):
        """
        Starts a craft_task. Returns the recipe used for crafting.
        Either `item` or `recipe` has to be given.
        """
        if recipe:
            item, meta, _ = recipe.result
        else:
            recipe = find_recipe(item, meta)
        if recipe:
            RunTask(self.craft_task(recipe, amount),
                    self.event.reg_event_handler, parent)
        return recipe

    def craft_task(self, recipe, amount=1):
        """
        Crafts `amount` items with `recipe`.
        Returns True if all items were crafted, False otherwise.
        (use `yield from` or `run_task(callback=cb)` to get the return value)
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
        # TODO is there a better way to get the grid width?
        grid_width = 3 if len(grid_slots) == 9 else 2
        # TODO check recipe size against grid size
        storage_slots = inv.window.persistent_slots

        # check materials for recipe
        total_amounts_needed = total_ingredient_amounts(recipe)
        for (mat_id, mat_meta), needed in total_amounts_needed.items():
            needed *= craft_times
            stored = inv.total_stored((mat_id, mat_meta), storage_slots)
            if needed > stored:
                raise TaskFailed('Missing %s:%s not stored, have %i of %i'
                                 % (mat_id, mat_meta, stored, needed))

        # TODO do not put back slot if still used
        # TODO check after each action if it succeeded
        # TODO use new helpers

        # iterates over a recipe's shape or ingredients
        def iter_shape():
            if recipe.in_shape:
                for y, row in enumerate(recipe.in_shape):
                    for x, (m_id, m_meta, m_amount) in enumerate(row):
                        slot = grid_slots[x + y * grid_width]
                        yield (slot, m_id, m_meta, m_amount)
            else:
                for slot, (m_id, m_meta, m_amount) \
                        in zip(grid_slots, recipe.ingredients):
                    yield (slot, m_id, m_meta, m_amount)

        # put materials into crafting grid
        for slot, mat_id, mat_meta, mat_amount in iter_shape():
            for i in range(mat_amount * craft_times):
                if inv.cursor_slot.amount < 1:
                    mat_slot = inv.find_slot((mat_id, mat_meta),
                                             storage_slots)
                    if not mat_slot:
                        raise TaskFailed('Craft: No %s:%s found in inventory'
                                         % (mat_id, mat_meta))
                    yield inv.async.click_slot(mat_slot)
                yield inv.async.click_slot(slot, right=True)
            # done putting in that item, put away
            if inv.cursor_slot.amount > 0:
                yield inv.async.store_or_drop()

        # take crafted items
        cursor_amt = inv.cursor_slot.amount
        crafted_amt = 0
        while crafted_amt + cursor_amt < amount:
            yield inv.async.click_slot(result_slot)
            # TODO check that cursor is non-empty, otherwise we did not craft
            if cursor_amt == inv.cursor_slot.amount:
                # cursor full, put away
                crafted_amt += cursor_amt
                yield inv.async.store_or_drop()
            cursor_amt = inv.cursor_slot.amount
        if inv.cursor_slot.amount > 0:
            # cursor still has items left from crafting, put away
            yield inv.async.store_or_drop()

        # put materials left from crafting back into inventory
        # TODO use inv.async.move_to_inventory
        for grid_slot in grid_slots:
            if grid_slot.amount > 0:
                yield inv.async.click_slot(grid_slot)
                if inv.cursor_slot.amount > 0:
                    yield inv.async.store_or_drop()

        # TODO return anything?
