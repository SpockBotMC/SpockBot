from spock.mcp.packet import Packet
from spock.mcp.utils import ByteToHex

mypacket = Packet(ident = 02, data = {
	'protocol_version': 51,
	'username': 'nickelpro',
	'host': 'localhost',
	'port': 25565,
	})

print ByteToHex(mypacket.encode())