import select

from spock.net.client import Client
from spock.mcp.mcpacket import Packet, read_packet
from spock.utils import ByteToHex
from spock.bound_buffer import BoundBuffer, BufferUnderflowException
from login import username, password

client = Client()
bbuff = BoundBuffer()
client.login(username, password, 'untamedears.com')
while True:
	while not client.poll.poll()[0][1]&select.POLLIN:
		pass
	bbuff.append(client.decipher.decrypt(client.sock.recv(4096)))
	bbuff.save()
	try:
		p = read_packet(bbuff)
		if p.ident == 0:
			while not client.poll.poll()[0][1]&select.POLLOUT:
				pass
			client.sock.send(client.encipher.encrypt(Packet(ident = 0x00, data = {
				'value': p.data['value']
				}).encode())
			)
		print p
	except BufferUnderflowException:
		bbuff.revert()