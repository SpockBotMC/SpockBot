from spock.client import Client
from spock.plugins.defaults import DefaultPlugins
from demoplugin import DemoPlugin
from login import username, password

plugins = DefaultPlugins
plugins.append(DemoPlugin)
client = Client(plugins = plugins, username = username, password = password)
client.start()