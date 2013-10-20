from spock.plugins import clientinfo, reflect, net, auth, start, world, timers

DefaultPlugins = [
	net.NetPlugin,
	auth.AuthPlugin,
	clientinfo.ClientInfoPlugin,
	reflect.ReflectPlugin,
	world.WorldPlugin,
	timers.TimerPlugin,
	start.StartPlugin,
]