from mcp.utils import ByteToHex
from mcp import datautils
from mcp.packet import Packet, read_packet
from mcp.bound_buffer import BoundBuffer
from login import username

host='localhost'
port=25565

data = {
	'protocol_version': 49,
	'username': username,
	'server_host': host,
	'server_port': port,
}
bbuff = BoundBuffer()

bbuff.append(Packet(ident = 02, data = data).encode())
print read_packet(bbuff).data