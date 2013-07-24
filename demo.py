from spock.net.client import Client
from plugins import DebugPlugin, ReConnect, EchoPacket, Gravity, AntiAFK
from login import username, password

plugins = [EchoPacket.EchoPacketPlugin]
client = Client(plugins = plugins, username = username, password = password)
client.start()