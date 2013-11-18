from spock import clsettings

class PluginLoader:
	def __init__(self, client, plugins):
		self.client = client
		self.plugins = plugins
		self.event_handlers = {}
		self.extensions = {'Client': self.client}
		self.announce = {}

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
			plugin(self, self.client.plugin_settings.get(plugin, None))

	def requires(self, ident):
		if ident not in self.extensions:
			if ident in self.announce:
				plugin = self.announce[ident]
				self.plugins.remove(plugin)
				plugin(self, self.client.plugin_settings.get(plugin, None))
			else:
				return None
		return self.extensions[ident]

	def provides(self, ident, obj):
		self.extensions[ident] = obj

class Client(object):
	def __init__(self, **kwargs):
		#Grab some settings
		self.settings = clsettings.SettingsDummy()
		settings = kwargs.get('settings', {})
		for setting in clsettings.defstruct:
			val = kwargs.get(setting[1], settings.get(setting[1], setting[2]))
			setattr(self, setting[0], val)

		PluginLoader(self, self.plugins)