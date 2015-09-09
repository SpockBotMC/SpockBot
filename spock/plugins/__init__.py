from spock.plugins.core import auth, event, net, ticker, timer
from spock.plugins.helpers import clientinfo, entities, interact, inventory,\
    keepalive, move, pathfinding, physics, respawn, start, world

from spock.plugins.base import PluginBase  # noqa


core_plugins = [
    ('auth', auth.AuthPlugin),
    ('event', event.EventPlugin),
    ('net', net.NetPlugin),
    ('ticker', ticker.TickerPlugin),
    ('timers', timer.TimerPlugin),
]
helper_plugins = [
    ('clientinfo', clientinfo.ClientInfoPlugin),
    ('entities', entities.EntityPlugin),
    ('interact', interact.InteractPlugin),
    ('inventory', inventory.InventoryPlugin),
    ('keepalive', keepalive.KeepalivePlugin),
    ('move', move.MovementPlugin),
    ('path', pathfinding.PathPlugin),
    ('physics', physics.PhysicsPlugin),
    ('respawn', respawn.RespawnPlugin),
    ('start', start.StartPlugin),
    ('world', world.WorldPlugin),
]
default_plugins = core_plugins + helper_plugins
DefaultPlugins = default_plugins  # for compatibility
