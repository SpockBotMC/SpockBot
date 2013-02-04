from spock.net.client import Client
from plugins.EchoPacket import EchoPacketPlugin
from login import username, password

plugins = [EchoPacketPlugin]
client = Client(plugins)
client.start(username, password)