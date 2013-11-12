from spock.plugins.core import net, auth, world, timers, keepalive
from spock.plugins.helpers import clientinfo, events, move, start

DefaultPlugins = [
	net.NetPlugin,
	auth.AuthPlugin,
	world.WorldPlugin,
	timers.TimerPlugin,
	keepalive.KeepalivePlugin,
	clientinfo.ClientInfoPlugin,
	#events.EventPlugin,
	#move.MovePlugin,
	start.StartPlugin,
]