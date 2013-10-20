from spock.plugins.defaults import DefaultPlugins

#2 values = Attribute&Setting name, default value
#3 values = Attribute name, setting name, default value
defstruct = [
	('plugins', DefaultPlugins),
	('plugin_settings', {}),
	('mc_username', 'username', 'Bot'),
	('mc_password', 'password', ''),
	('daemon', False),
	('logfile', ''),
	('pidfile', ''),
	('authenticated', True),
	('bufsize', 4096),
	('sock_quit', True),
	('sess_quit', True),
	('proxy', {
		'enabled': False,
		'host': '',
		'port': 0,
	}),
]

class SettingsDummy:
	pass

for index, setting in enumerate(defstruct):
	if len(setting) == 2:
		defstruct[index] = (setting[0], setting[0], setting[1])