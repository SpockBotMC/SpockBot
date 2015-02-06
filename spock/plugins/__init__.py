from spock.plugins.core import event, net, auth, timer, ticker
from spock.plugins.helpers import start, keepalive, clientinfo, world, move, respawn, physics, inventory

DefaultPlugins = [
	('event', event.EventPlugin),
	('net', net.NetPlugin),
	('auth', auth.AuthPlugin),
	('ticker', ticker.TickerPlugin),
	('timer', timer.TimerPlugin),
	('start', start.StartPlugin),
	('keepalive', keepalive.KeepalivePlugin),
	('respawn', respawn.RespawnPlugin),
	('move', move.MovementPlugin),
	('world', world.WorldPlugin),
	('client', clientinfo.ClientInfoPlugin),
	('physics', physics.PhysicsPlugin),
	('inventory', inventory.InventoryPlugin),
]
