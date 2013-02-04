from spock.mcp.mcpacket import Packet, read_packet
from spock.bound_buffer import BoundBuffer
from spock.mcp import mcdata

p = Packet(ident = 02, data = {
        'protocol_version': mcdata.MC_PROTOCOL_VERSION,
        'username': 'nickelpro',
        'host': 'localhost',
        'port': 25565,
            })

b = Packet(ident = 0xC9, data = {
    'player_name': 'nickelpro',
    'online': True, 
    'ping': 52
    })

bbuff = BoundBuffer(p.encode() + b.encode())

packet = read_packet(bbuff)
print packet

packet = read_packet(bbuff)
print packet