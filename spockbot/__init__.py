import logging

from spockbot.plugins.loader import PluginLoader as Client  # noqa

logger = logging.getLogger('spockbot')
logger.setLevel(logging.INFO)
default_handler = logging.StreamHandler()
formatter = logging.Formatter('[%(levelname)s]: %(message)s')
default_handler.setFormatter(formatter)
logger.addHandler(default_handler)
