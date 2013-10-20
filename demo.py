from spock.net.client import Client
from spock.plugins.defaults import DefaultPlugins
from plugins import DebugPlugin
from login import username, password

plugins = DefaultPlugins
plugins.extend([DebugPlugin.TestRequire3, DebugPlugin.DebugPlugin, DebugPlugin.TestRequire1])
client = Client(plugins = plugins, username = username, password = password)
client.start(host='mc.civcraft.vg')