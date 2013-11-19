from spock.plugins import DefaultPlugins

class PluginLoader:
	def __init__(self, client, settings):
		self.plugins = settings['plugins']
		del settings['plugins']
		self.plugin_settings = settings['plugin_settings']
		del settings['plugin_settings']
		self.announce = {}
		self.extensions = {
			'Client': client,
			'Settings': settings
		}

		for plugin in self.plugins:
			if hasattr(plugin, 'pl_announce'):
				for ident in plugin.pl_announce:
					self.announce[ident] = plugin
		# Make an attempt at providing the reg_event_handler API
		# But we can't guarantee it will be there (Ha!)
		event = self.requires('Event')
		self.reg_event_handler = event.reg_event_handler if event else None
		while self.plugins:
			plugin = self.plugins.pop()
			plugin(self, self.plugin_settings.get(plugin, None))

	def requires(self, ident):
		if ident not in self.extensions:
			if ident in self.announce:
				plugin = self.announce[ident]
				self.plugins.remove(plugin)
				plugin(self, self.plugin_settings.get(plugin, None))
			else:
				return None
		return self.extensions[ident]

	def provides(self, ident, obj):
		self.extensions[ident] = obj

#2 values = Attribute&Setting name, default value
#3 values = Attribute name, setting name, default value
default_settings = [
	('plugins', DefaultPlugins),
	('plugin_settings', {}),
	('mc_username', 'username', 'Bot'),
	('mc_password', 'password', ''),
	('authenticated', True),
	('bufsize', 4096),
	('sock_quit', True),
	('sess_quit', True),
]

for index, setting in enumerate(default_settings):
	if len(setting) == 2:
		default_settings[index] = (setting[0], setting[0], setting[1])

class Client:
	def __init__(self, **kwargs):
		#Grab some settings
		settings = kwargs.get('settings', {})
		final_settings = {}
		for setting in default_settings:
			val = kwargs.get(setting[1], settings.get(setting[1], setting[2]))
			final_settings[setting[0]] = val

		PluginLoader(self, final_settings)