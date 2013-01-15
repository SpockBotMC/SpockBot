import socket
from spock.mcp.bound_buffer import BoundBuffer
from spock.mcp.packet import Packet, read_packet
from spock.mcp.mcdata import SERVER_LIST_PING_MAGIC
from spock.mcp.utils import DecodeServerListPing

def get_info(host='localhost', port=25565):
	#Set up our socket
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((host, port))
	
	#Make our buffer
	bbuff = BoundBuffer()

	#Send 0xFE: Server list ping
	s.send(Packet(ident = 0xFE, data = {
		'Magic': SERVER_LIST_PING_MAGIC,
		}).encode()
	)
	
	#Read some data
	bbuff.append(s.recv(1024))

	#We don't need the socket anymore
	s.close()

	#Read a packet out of our buffer
	packet = read_packet(bbuff)

	#This particular packet is a special case, so we have
	#a utility function do a second decoding step.
	return DecodeServerListPing(packet)

print get_info(host = 'untamedears.com')