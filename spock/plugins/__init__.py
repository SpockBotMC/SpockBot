from spock.plugins.core import event, net, auth, timer
from spock.plugins.helpers import start, keepalive, clientinfo, world, move, respawn

DefaultPlugins = [
	event.EventPlugin,
	net.NetPlugin,
	auth.AuthPlugin,
	timer.TimerPlugin,
	start.StartPlugin,
	keepalive.KeepalivePlugin,
	respawn.RespawnPlugin,
	move.MovementPlugin,
	#world.WorldPlugin,
	#clientinfo.ClientInfoPlugin,
]
