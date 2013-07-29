default_settings = {
	'plugins': [],         #Plugins
	'plugin_settings': {}, #Extra settings for plugins
	'username': 'Bot',     #minecraft.net username or name for unauthenticated servers
	'password': '',	       #Password for account, ignored if not authenticated
	'daemon': False,       #Run bot as daemon
	'logfile': '',         #Where to put logfile for daemon
	'pidfile': '',         #Where to put pidfile for daemon
	'authenticated': True, #Authenticate with minecraft.net
	'bufsize': 4096,       #Size of socket buffer
	'timeout': -1,         #Poll timeout, only change if necessary for plugin
	'sock_quit': True,     #Stop bot on socket error or hangup
	'sess_quit': True,     #Stop bot on failed session login
	'proxy': {             #!!WILL BREAK!! Proxy server to forward through, unimplemented
		'enabled': False,
		'host': '',
		'port': 0,
	},

}