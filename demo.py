from spock.net.client import Client
from plugins import DebugPlugin, ReConnect, EchoPacket, Gravity, AntiAFK
from login import username, password

plugins = [ReConnect.ReConnectPlugin, DebugPlugin.DemoDebug, AntiAFK.AntiAFKPlugin]
client = Client(plugins = plugins)
client.start(username, password)