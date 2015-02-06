from spock.plugins.pluginloader import PluginLoader

import logging
logger = logging.getLogger('spock')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

Client = PluginLoader
