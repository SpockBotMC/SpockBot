from spock.plugins.defaults import DefaultPlugins

default_settings = {
	'username': 'Bot',     #minecraft.net username or name for unauthenticated servers
	'password': '',	       #Password for account, ignored if not authenticated
	'authenticated': True, #Authenticate with authserver.mojang.com
	'bufsize': 4096,       #Size of socket buffer
	'sock_quit': True,     #Stop bot on socket error or hangup
	'sess_quit': True,     #Stop bot on failed session login
	'thread_workers': 5,   #Number of workers in the thread pool
	'plugins': DefaultPlugins,         #Plugins
	'plugin_settings': {}, #Extra settings for plugins
}