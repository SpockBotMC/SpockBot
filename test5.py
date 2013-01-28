import socket
import select
import thread
import time
from spock.mcp.bound_buffer import BoundBuffer
from spock.mcp.packet import Packet, read_packet
from spock.mcp.mcdata import SERVER_LIST_PING_MAGIC
from spock.mcp.utils import DecodeSLP
from spock.net.mcsocket import AsyncSocket

def get_info(host='localhost', port=25565):
	#Set up our socket
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setblocking(0)
	try:
		s.connect((host, port))
	except socket.error as error:
		print "Error on Connect (this is normal): " + str(error)
	poll = select.poll()
	poll.register(s)
	
	#Make our buffer
	bbuff = BoundBuffer()

	#Send 0xFE: Server list ping
	while not select.POLLOUT&poll.poll()[0][1]:
		pass
	s.send(Packet(ident = 0xFE, data = {
		'magic': SERVER_LIST_PING_MAGIC,
		}).encode()
	)
	
	#Read some data
	while not select.POLLIN&poll.poll()[0][1]:
		pass
	print poll.poll()
	bbuff.append(s.recv(4096))
	#We don't need the socket anymore
	s.close()
	#Read a packet out of our buffer
	packet = read_packet(bbuff)
	#This particular packet is a special case, so we have
	#a utility function do a second decoding step.
	return DecodeSLP(packet)

print get_info(host = 'untamedears.com')