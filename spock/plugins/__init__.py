from spock.plugins.core import auth, event, net, ticker, timer
from spock.plugins.helpers import chat, clientinfo, entities, interact, \
    inventory, keepalive, movement, physics, respawn, start, taskmanager, world
from spock.plugins.base import PluginBase  # noqa


core_plugins = [
    ('auth', auth.AuthPlugin),
    ('event', event.EventPlugin),
    ('net', net.NetPlugin),
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
    ('physics', physics.PhysicsPlugin),
    ('respawn', respawn.RespawnPlugin),
    ('start', start.StartPlugin),
    ('taskmanager', taskmanager.TaskManager),
    ('world', world.WorldPlugin),
]
default_plugins = core_plugins + helper_plugins
