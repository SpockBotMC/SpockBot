from spock.net.client import Client
from plugins import DebugPlugin, ReConnect, EchoPacket, Gravity
from login import username, password

plugins = [ReConnect.ReConnectPlugin, DebugPlugin.DebugPlugin, Gravity.GravityPlugin]
client = Client(plugins)
client.start(username, password)