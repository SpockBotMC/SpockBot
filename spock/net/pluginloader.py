class PluginLoader:
	def __init__(self, client, plugins):
		self.client = client
		self.plugins = plugins
		self.extensions = {'Client': self.client}
		self.announce = {}

		for plugin in self.plugins:
			if hasattr(plugin, 'pl_announce'):
				for ident in plugin.pl_announce:
					self.announce[ident] = plugin
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

	def reg_event_handler(self, events, handlers):
		self.client.reg_event_handler(events, handlers)