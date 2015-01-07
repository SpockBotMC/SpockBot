from spock.plugins.core import event, net, auth, timer, ticker
from spock.plugins.helpers import start, keepalive, clientinfo, world, move, respawn, physics

DefaultPlugins = [
	event.EventPlugin,
	net.NetPlugin,
	auth.AuthPlugin,
	ticker.TickerPlugin,
	timer.TimerPlugin,
	start.StartPlugin,
	keepalive.KeepalivePlugin,
	respawn.RespawnPlugin,
	move.MovementPlugin,
	world.WorldPlugin,
	clientinfo.ClientInfoPlugin,
	physics.PhysicsPlugin,
]
