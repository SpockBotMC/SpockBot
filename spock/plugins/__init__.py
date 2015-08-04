from spock.plugins.core import event, net, auth, timer, ticker
from spock.plugins.helpers import start, keepalive, clientinfo, entities, world, move, respawn, physics, inventory

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
]

