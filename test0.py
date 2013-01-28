from spock.mcp.packet import Packet, read_packet
from spock.mcp.bound_buffer import BoundBuffer
from spock.mcp import mcdata

p = Packet(ident = 02, data = {
        'protocol_version': mcdata.MC_PROTOCOL_VERSION,
        'username': 'nickelpro',
        'host': 'localhost',
        'port': 25565,
            })

bbuff = BoundBuffer(p.encode())

d = read_packet(bbuff)

print d