import select

from spock.net.client import Client
from spock.mcp.mcpacket import Packet, read_packet
from spock.utils import ByteToHex
from spock.bound_buffer import BoundBuffer, BufferUnderflowException
from login import username, password

client = Client()
client.login(username, password, 'untamedears.com')