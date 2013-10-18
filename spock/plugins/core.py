from spock import utils, bound_buffer
from spock.mcp import mcpacket

class CoreClientPlugin:
	def __init__(self, ploader, settings):
		self.client = ploader.requires('Client')
		ploader.reg_event_handler('SOCKET_RECV', self.handleRECV)
		ploader.reg_event_handler('SOCKET_SEND', self.handleSEND)
		ploader.reg_event_handler('SOCKET_ERR', self.handleERR)
		ploader.reg_event_handler('SOCKET_HUP', self.handleHUP)

	#SOCKET_RECV - Socket is ready to recieve data
	def handleRECV(self, name, event):
		try:
			data = self.client.sock.recv(self.client.bufsize)
			self.client.rbuff.append(
				self.client.cipher.decrypt(data) if self.client.encrypted else data
			)
		except socket.error as error:
			#TODO: Do something here?
			pass
		try:
			while True:
				self.client.rbuff.save()
				packet = mcpacket.read_packet(self.client.rbuff)
				self.client.emit(packet.ident, packet)
		except bound_buffer.BufferUnderflowException:
			self.client.rbuff.revert()

	#SOCKET_SEND - Socket is ready to send data and Send buffer contains data to send
	def handleSEND(self, name, event):
		try:
			sent = self.client.sock.send(self.client.sbuff)
			self.client.sbuff = self.client.sbuff[sent:]
		except socket.error as error:
			#TODO: Do something here?
			pass

	#SOCKET_ERR - Socket Error has occured
	def handleERR(self, name, event):
		if self.client.sock_quit and not self.client.kill:
			print("Socket Error has occured, stopping...")
			self.client.kill = True
		self.client.reset()

	#SOCKET_HUP - Socket has hung up
	def handleHUP(self, name, event):
		if self.client.sock_quit and not self.client.kill:
			print("Socket has hung up, stopping...")
			self.client.kill = True
		self.client.reset()
