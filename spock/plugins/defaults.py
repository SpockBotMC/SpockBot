from spock.plugins import clientinfo, reflect, net, auth, start

DefaultPlugins = [
	net.NetPlugin,
	auth.AuthPlugin,
	clientinfo.ClientInfoPlugin,
	reflect.ReflectPlugin,
	start.StartPlugin
]