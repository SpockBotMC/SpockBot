import socket
import logging
from spock.mcp.mcpacket import read_packet, Packet
from spock.net.cflags import cflags
from spock.bound_buffer import BufferUnderflowException
from spock import utils

fhandles = {}
def fhandle(ident):
	def inner(cl):
		fhandles[ident] = cl
		return cl
	return inner

#SOCKET_ERR - Socket Error has occured
@fhandle('SOCKET_ERR')
def handleERR(client):
	if client.sock_quit and not client.kill:
		print("Socket Error has occured, stopping...")
		client.kill = True
	utils.ResetClient(client)

#SOCKET_HUP - Socket has hung up
@fhandle('SOCKET_HUP')
def handleHUP(client):
	if client.sock_quit and not client.kill:
		print("Socket has hung up, stopping...")
		client.kill = True
	utils.ResetClient(client)

#SOCKET_RECV - Socket is ready to recieve data
@fhandle('SOCKET_RECV')
def handleSRECV(client):
	try:
		data = client.sock.recv(client.bufsize)
		client.rbuff.append(client.cipher.decrypt(data) if client.encrypted else data)
	except socket.error as error:
		logging.info(str(error))
	try:
		while True:
			client.rbuff.save()
			packet = read_packet(client.rbuff)
			client.emit(packet.ident, packet)
	except BufferUnderflowException:
		client.rbuff.revert()

#SOCKET_SEND - Socket is ready to send data and Send buffer contains data to send
@fhandle('SOCKET_SEND')
def handleSEND(client):
	try:
		sent = client.sock.send(client.sbuff)
		client.sbuff = client.sbuff[sent:]
	except socket.error as error:
		logging.info(str(error))