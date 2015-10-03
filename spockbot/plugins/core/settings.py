from spockbot.plugins import default_plugins
from spockbot.plugins.base import get_settings, pl_announce


class PloaderFetch(object):
    def __init__(self, plugins, plugin_settings):
        self.plugins = plugins
        self.plugin_settings = plugin_settings

    def get_plugins(self):
        return self.plugins

    def get_plugin_settings(self, plugin):
        return self.plugin_settings.get(plugin, {})


@pl_announce('PloaderFetch')
class SettingsPlugin(object):
    def __init__(self, ploader, kwargs):
        settings = get_settings(kwargs.get('settings', {}), kwargs)
        plugin_list = settings.get('plugins', default_plugins)
        plugins = []
        plugin_settings = {}
        for plugin in plugin_list:
            plugins.append(plugin[1])
            plugin_settings[plugin[1]] = settings.get(plugin[0], {})
        ploader.provides('PloaderFetch',
                         PloaderFetch(plugins, plugin_settings))
