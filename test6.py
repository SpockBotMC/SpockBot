from spock.net.client import Client
from spock.mcp.utils import ByteToHex
from spock.mcp.bound_buffer import BoundBuffer, BufferUnderflowException
from spock.mcp.packet import Packet, read_packet
from login import username, password
import select

client = Client()
bbuff = BoundBuffer()
client.login(username, password)
while True:
	while not client.poll.poll()[0][1]&select.POLLIN:
		pass
	bbuff.append(client.cipher.decrypt(client.socket.recv(4096)))
	bbuff.save()
	try:
		p = read_packet(bbuff)
		bbuff.save()
		print p.data
	except BufferUnderflowException:
		bbuff.revert()