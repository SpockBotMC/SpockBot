from spock.plugins.defaults import DefaultPlugins

default_settings = {
	'username': 'Bot',     #minecraft.net username or name for unauthenticated servers
	'password': '',	       #Password for account, ignored if not authenticated
	'authenticated': True, #Authenticate with authserver.mojang.com
	'bufsize': 4096,       #Size of socket buffer
	'sock_quit': True,     #Stop bot on socket error or hangup
	'sess_quit': True,     #Stop bot on failed session login
	'proxy': {             #!!WILL BREAK!! Proxy server to forward through, unimplemented
		'enabled': False,
		'host': '',
		'port': 0,
	},
	'plugins': [*DefaultPlugins],         #Plugins
	'plugin_settings': {}, #Extra settings for plugins
}