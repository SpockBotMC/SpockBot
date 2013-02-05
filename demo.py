from spock.net.client import Client
from plugins import DebugPlugin, ReConnect, EchoPacket
from login import username, password

plugins = [ReConnect.ReConnectPlugin, EchoPacket.EchoPacketPlugin]
client = Client(plugins)
client.start(username, password)