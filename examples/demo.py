from spock.net.client import Client
from demoplugin import DemoPlugin
from login import username, password

plugins = DefaultPlugins
plugins.extend(DemoPlugin)
client = Client(plugins = plugins, username = username, password = password)
client.start()