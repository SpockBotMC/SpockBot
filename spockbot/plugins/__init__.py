from spockbot.plugins.core import auth, event, net, taskmanager, ticker, timer
from spockbot.plugins.helpers import chat, clientinfo, entities, interact, \
    inventory, keepalive, movement, pathfinding, physics, respawn, start, world


core_plugins = [
    ('auth', auth.AuthPlugin),
    ('event', event.EventPlugin),
    ('net', net.NetPlugin),
    ('taskmanager', taskmanager.TaskManager),
    ('ticker', ticker.TickerPlugin),
    ('timers', timer.TimerPlugin),
]
helper_plugins = [
    ('chat', chat.ChatPlugin),
    ('clientinfo', clientinfo.ClientInfoPlugin),
    ('entities', entities.EntitiesPlugin),
    ('interact', interact.InteractPlugin),
    ('inventory', inventory.InventoryPlugin),
    ('keepalive', keepalive.KeepalivePlugin),
    ('movement', movement.MovementPlugin),
    ('path', pathfinding.PathPlugin),
    ('physics', physics.PhysicsPlugin),
    ('respawn', respawn.RespawnPlugin),
    ('start', start.StartPlugin),
    ('world', world.WorldPlugin),
]
default_plugins = core_plugins + helper_plugins
