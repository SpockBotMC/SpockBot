from spock.client import Client
from spock.plugins import DefaultPlugins
from demoplugin import DemoPlugin
#Open login.py and put in your username and password
from login import username, password

plugins = DefaultPlugins
plugins.append(DemoPlugin)
client = Client(plugins = plugins, username = username, password = password)
client.start()