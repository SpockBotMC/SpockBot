from spock.plugins.core import net, auth, world, timers, reflect
from spock.plugins.helpers import clientinfo, events, move, start

DefaultPlugins = [
	net.NetPlugin,
	auth.AuthPlugin,
	world.WorldPlugin,
	timers.TimerPlugin,
	reflect.ReflectPlugin,
	clientinfo.ClientInfoPlugin,
	#events.EventPlugin,
	#move.MovePlugin,
	start.StartPlugin,
]