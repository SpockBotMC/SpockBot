import socket
from spock.mcp import datautils
from spock.utils import BoundBuffer, ByteToHex

sock = socket.socket()
handshake = datautils.pack('varint', 0x00) + datautils.pack('varint', 4) + datautils.pack('string', 'localhost') + datautils.pack('ushort', 25565) + datautils.pack('varint', 0x02)
handshake = datautils.pack('varint', len(handshake)) + handshake
login_start = datautils.pack('varint', 0x00) + datautils.pack('string', 'nickelpro')
login_start = datautils.pack('varint', len(login_start)) + login_start
sock.connect(('localhost', 25565))
sent = sock.send(handshake)
print(ByteToHex(handshake))
print(len(handshake), sent)
sent = sock.send(login_start)
print(ByteToHex(login_start))
print(len(login_start), sent)
print(ByteToHex(sock.recv(4096)))
