"""
Provides reasonably not-awful plugin loading
"""
from spock.plugins.core.settings import SettingsPlugin
import traceback
import logging
logger = logging.getLogger('spock')

base_warn = "PluginLoader could not satisfy %s dependency for %s"
pl_warn = base_warn + ": %s"

class PluginLoader:
    def __init__(self, **kwargs):
        self.announce = {}
        self.extensions = {}
        self.events = []
        kwargs.get('settings_mixin', SettingsPlugin)(self, kwargs)
        self.fetch = self.requires('PloaderFetch')
        self.plugins = self.fetch.get_plugins()

        for plugin in self.plugins:
            if hasattr(plugin, 'pl_announce'):
                for ident in plugin.pl_announce:
                    self.announce[ident] = plugin
            if hasattr(plugin, 'pl_event'):
                for ident in plugin.pl_event:
                    self.events.append(ident)

        event = self.requires('Event')
        self.reg_event_handler = event.reg_event_handler if event else None
        while self.plugins:
            plugin = self.plugins.pop()
            try:
                plugin(self, self.fetch.get_plugin_settings(plugin))
            except Exception as e:
                logger.error('LOADER: Plugin %s failed to load', plugin.__name__)
                print(traceback.format_exc())


    def requires(self, ident, soft = False, warning = None):
        if ident not in self.extensions:
            if ident in self.announce:
                plugin = self.announce[ident]
                self.plugins.remove(plugin)
                plugin(self, self.fetch.get_plugin_settings(plugin))
            elif ident in self.events:
                return True
            else:
                softness = "soft" if soft else "hard"
                if warning:
                    logger.warn(pl_warn, softness, ident, warning)
                else:
                    logger.warn(base_warn, softness, ident)
                return None
        return self.extensions[ident]

    def provides(self, ident, obj):
        self.extensions[ident] = obj
