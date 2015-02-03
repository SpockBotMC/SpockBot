"""
Basic demo example
"""

from spock import Client
from spock.plugins import DefaultPlugins
from demoplugin import DemoPlugin
#Open login.py and put in your username and password
from login import username, password

plugins = DefaultPlugins
plugins.append(DemoPlugin)
client = Client(plugins = plugins, username = username, password = password)
#client.start() with no arguments will automatically connect to localhost
client.start('localhost', 25565)
