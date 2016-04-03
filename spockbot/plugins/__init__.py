from spockbot.plugins.core import auth, event, net, select, \
    taskmanager, ticker, timers
from spockbot.plugins.helpers import auxiliary, channels, chat, clientinfo, \
    craft, entities, interact, inventory, movement, \
    pathfinding, physics, start, world

core_plugins = [
    ('auth', auth.AuthPlugin),
    ('event', event.EventPlugin),
    ('net', net.NetPlugin),
    ('select', select.SelectPlugin),
    ('taskmanager', taskmanager.TaskManager),
    ('ticker', ticker.TickerPlugin),
    ('timers', timers.TimersPlugin),
]
helper_plugins = [
    ('auxiliary', auxiliary.AuxiliaryPlugin),
    ('channels', channels.ChannelsPlugin),
    ('chat', chat.ChatPlugin),
    ('clientinfo', clientinfo.ClientInfoPlugin),
    ('craft', craft.CraftPlugin),
    ('entities', entities.EntitiesPlugin),
    ('interact', interact.InteractPlugin),
    ('inventory', inventory.InventoryPlugin),
    ('movement', movement.MovementPlugin),
    ('pathfinding', pathfinding.PathfindingPlugin),
    ('physics', physics.PhysicsPlugin),
    ('start', start.StartPlugin),
    ('world', world.WorldPlugin),
]
default_plugins = core_plugins + helper_plugins
