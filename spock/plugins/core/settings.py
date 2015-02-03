from spock.utils import pl_announce
from spock.plugins import DefaultPlugins

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

class PloaderFetch:
	def __init__(self, final_settings):
		self.plugins = final_settings['plugins']
		self.plugin_settings = final_settings['plugin_settings']

	def get_plugins(self):
		return self.plugins

	def get_plugin_settings(self, plugin):
		return self.plugin_settings.get(plugin, {})

@pl_announce('Settings', 'PloaderFetch')
class SettingsPlugin:
	def __init__(self, ploader, kwargs):
		settings = kwargs.get('settings', {})
		final_settings = {}
		for setting in default_settings:
			val = kwargs.get(setting[1], settings.get(setting[1], setting[2]))
			final_settings[setting[0]] = val
		ploader.provides('PloaderFetch', PloaderFetch(final_settings))
		del final_settings['plugins']
		del final_settings['plugin_settings']
		ploader.provides('Settings', final_settings)
