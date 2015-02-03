"""
Offline connection demo
"""

from spock import Client
from spock.plugins import DefaultPlugins
from demoplugin import DemoPlugin
#Open login.py and put in your username and password
from login import username

plugins = DefaultPlugins
plugins.append(DemoPlugin)
client = Client(plugins = plugins, username = username, authenticated=False)
#client.start() with no arguments will automatically connect to localhost
client.start('localhost', 25565)
