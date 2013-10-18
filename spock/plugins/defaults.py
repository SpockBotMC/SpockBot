from spock.plugins import clientinfo, reflect, core, auth

DefaultPlugins = [
	core.CoreClientPlugin,
	auth.AuthPlugin,
	clientinfo.ClientInfoPlugin,
	reflect.ReflectPlugin,
]