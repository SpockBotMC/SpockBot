import socket
import logging
from spock.mcp.mcpacket import read_packet, Packet
from spock.bound_buffer import BufferUnderflowException
from spock import utils
from cflags import cflags

fhandles = {}
def fhandle(ident):
	def inner(cl):
		fhandles[ident] = cl
		return cl
	return inner

#SOCKET_ERR - Socket Error has occured
@fhandle(cflags['SOCKET_ERR'])
def handleERR(client):
	#print "Socket Error has occured"
	utils.ResetClient(client)

#SOCKET_HUP - Socket has hung up
@fhandle(cflags['SOCKET_HUP'])
def handleHUP(client):
	#print "Socket has hung up"
	utils.ResetClient(client)

#SOCKET_RECV - Socket is ready to recieve data
@fhandle(cflags['SOCKET_RECV'])
def handleSRECV(client):
	try:
		data = client.sock.recv(client.bufsize)
		client.rbuff.append(client.cipher.decrypt(data) if client.encrypted else data)
	except socket.error as error:
		logging.info(str(error))

#SOCKET_SEND - Socket is ready to send data and Send buffer contains data to send
@fhandle(cflags['SOCKET_SEND'])
def handleSEND(client):
	try:
		sent = client.sock.send(client.sbuff)
		client.sbuff = client.sbuff[sent:]
	except socket.error as error:
		logging.info(str(error))

#RBUFF_RECV - Read buffer has data ready to be unpacked
@fhandle(cflags['RBUFF_RECV'])
def handleBRECV(client):
	try:
		while True:
			client.rbuff.save()
			packet = read_packet(client.rbuff)
			client.dispatch_packet(packet)
	except BufferUnderflowException:
		client.rbuff.revert()