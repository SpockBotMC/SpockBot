
from spock.mcp.mcpacket import read_packet
from spock.bound_buffer import BufferUnderflowException

fhandles = {}
def fhandle(ident):
	def inner(cl):
		fhandles[ident] = cl
		return cl
	return inner

#SOCKET_RECV - Socket is ready to recieve data
@fhandle(0x01)
def handle01(client):
	data = client.sock.recv(client.bufsize)
	client.rbuff.append(client.cipher.decrypt(data) if client.encrypted else data)
	client.rbuff.save()

#SOCKET_SEND - Socket is ready to send data and Send buffer contains data to send
@fhandle(0x02)
def handle02(client):
	sent = client.sock.send(client.sbuff)
	client.sbuff = client.sbuff[sent:]

#RBUFF_RECV - Read buffer has data ready to be unpacked
@fhandle(0x04)
def handle04(client):
	try:
		packet = read_packet(client.rbuff)
		client.dispatch_packet(packet)
	except BufferUnderflowException:
		client.rbuff.revert()