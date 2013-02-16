from spock.mcp.mcpacket import read_packet
from spock.bound_buffer import BufferUnderflowException
from cflags import cflags

fhandles = {}
def fhandle(ident):
	def inner(cl):
		fhandles[ident] = cl
		return cl
	return inner

#SOCKET_RECV - Socket is ready to recieve data
@fhandle(cflags['SOCKET_RECV'])
def handle01(client):
	data = client.sock.recv(client.bufsize)
	client.rbuff.append(client.cipher.decrypt(data) if client.encrypted else data)

#SOCKET_SEND - Socket is ready to send data and Send buffer contains data to send
@fhandle(cflags['SOCKET_SEND'])
def handle02(client):
	sent = client.sock.send(client.sbuff)
	client.sbuff = client.sbuff[sent:]

#RBUFF_RECV - Read buffer has data ready to be unpacked
@fhandle(cflags['RBUFF_RECV'])
def handle04(client):
	try:
		while True:
			client.rbuff.save()
			packet = read_packet(client.rbuff)
			client.dispatch_packet(packet)
	except BufferUnderflowException:
		client.rbuff.revert()