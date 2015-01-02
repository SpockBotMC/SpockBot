from spock.plugins.core import event, net, auth
from spock.plugins.helpers import start, keepalive, clientinfo, world, move

DefaultPlugins = [
	event.EventPlugin,
	net.NetPlugin,
	auth.AuthPlugin,
	start.StartPlugin,
	keepalive.KeepalivePlugin,
	#world.WorldPlugin,
	#clientinfo.ClientInfoPlugin,
	#move.MovePlugin,
]
