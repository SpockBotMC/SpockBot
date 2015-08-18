from spock.plugins.core import auth, event, net, ticker, timer
from spock.plugins.helpers import clientinfo, entities, interact, inventory,\
    keepalive, move, physics, respawn, start, world

DefaultPlugins = [
    ('event', event.EventPlugin),
    ('net', net.NetPlugin),
    ('auth', auth.AuthPlugin),
    ('ticker', ticker.TickerPlugin),
    ('timers', timer.TimerPlugin),
    ('start', start.StartPlugin),
    ('keepalive', keepalive.KeepalivePlugin),
    ('respawn', respawn.RespawnPlugin),
    ('move', move.MovementPlugin),
    ('world', world.WorldPlugin),
    ('clientinfo', clientinfo.ClientInfoPlugin),
    ('entities', entities.EntityPlugin),
    ('physics', physics.PhysicsPlugin),
    ('inventory', inventory.InventoryPlugin),
    ('interact', interact.InteractPlugin),
]
