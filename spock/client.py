"""
This file deserves some sort of explanation for why it exists and why
PluginLoader lives here, but its mostly just a holdover from the days when there
was a monolithic Client god-class that handled everything. The Client class is
gone now, but the file remains
"""
from spock.plugins.core.settings import SettingsPlugin

class PluginLoader:
	def __init__(self, **kwargs):
		self.announce = {}
		self.extensions = {}
		kwargs.get('settings_mixin', SettingsPlugin)(self, kwargs)
		self.fetch = self.requires('PloaderFetch')
		self.plugins = self.fetch.get_plugins()

		for plugin in self.plugins:
			if hasattr(plugin, 'pl_announce'):
				for ident in plugin.pl_announce:
					self.announce[ident] = plugin

		event = self.requires('Event')
		self.reg_event_handler = event.reg_event_handler if event else None
		while self.plugins:
			plugin = self.plugins.pop()
			plugin(self, self.fetch.get_plugin_settings(plugin))

	def requires(self, ident):
		if ident not in self.extensions:
			if ident in self.announce:
				plugin = self.announce[ident]
				self.plugins.remove(plugin)
				plugin(self, self.fetch.get_plugin_settings(plugin))
			else:
				return None
		return self.extensions[ident]

	def provides(self, ident, obj):
		self.extensions[ident] = obj

Client = PluginLoader
