import socket
from spock import utils
from spock.plugins.plutils import pl_announce
from spock.mcp import mcpacket
from Crypto.Cipher import AES

class AESCipher():
	def __init__(self, SharedSecret):
		self.encipher = AES.new(SharedSecret, AES.MODE_CFB, IV=SharedSecret)
		self.decipher = AES.new(SharedSecret, AES.MODE_CFB, IV=SharedSecret)

	def encrypt(self, data):
		return self.encipher.encrypt(data)

	def decrypt(self, data):
		return self.decipher.decrypt(data)

class NetCore:
	def __init__(self, client):
		self.client = client
		self.host = None
		self.port = None
		self.encrypted = False
		self.sbuff = b''
		self.rbuff = utils.BoundBuffer()

	def connect(self, host = 'localhost', port = 25565):
		self.host = host
		self.port = port
		try:
			print("Attempting to connect to host:", host, "port:", port)
			self.client.sock.connect((self.host, self.port))
		except socket.error as error:
			#print("Error on Connect (this is normal):", str(error))
			pass

	def push(self, packet):
		bytes = packet.encode()
		self.sbuff += (self.cipher.encrypt(bytes) if self.encrypted else bytes)
		self.client.emit(packet.ident, packet)
		self.client.send = True

	def enable_crypto(self, secret_key):
		self.cipher = AESCipher(secret_key)
		self.encrypted = True

	def disable_crypto(self):
		self.cipher = None
		self.encrypted = False

	def disconnect(self, force = False):
		if force:
			self.client.sock.close()
			return

		flags = self.client.get_flags()
		if 'SOCKET_HUP' not in flags:
			self.push(mcpacket.Packet(ident = 0xFF, data = {
				'reason': 'disconnect.quitting'
			}))
			while self.sbuff:
				flags = self.client.get_flags()
				if ('SOCKET_ERR' in flags) or ('SOCKET_HUP' in flags):
					break
				elif 'SOCKET_SEND' in flags:
					self.client.emit('SOCKET_SEND')
		self.client.sock.close()

	def reset(self):
		self.client.net_reset()
		self.__init__(self.client)



@pl_announce('Net')
class NetPlugin:
	def __init__(self, ploader, settings):
		self.client = ploader.requires('Client')
		self.net = NetCore(self.client)
		ploader.provides('Net', self.net)
		ploader.reg_event_handler('SOCKET_RECV', self.handleRECV)
		ploader.reg_event_handler('SOCKET_SEND', self.handleSEND)
		ploader.reg_event_handler('SOCKET_ERR', self.handleERR)
		ploader.reg_event_handler('SOCKET_HUP', self.handleHUP)

	#SOCKET_RECV - Socket is ready to recieve data
	def handleRECV(self, name, event):
		try:
			data = self.client.sock.recv(self.client.bufsize)
			if not data: #Just because we have to support socket.select
				self.client.emit('SOCKET_HUP')
				return
			self.net.rbuff.append(
				self.net.cipher.decrypt(data) if self.net.encrypted else data
			)
		except socket.error as error:
			#TODO: Do something here?
			pass
		try:
			while True:
				self.net.rbuff.save()
				packet = mcpacket.read_packet(self.net.rbuff)
				self.client.emit(packet.ident, packet)
		except utils.BufferUnderflowException:
			self.net.rbuff.revert()

	#SOCKET_SEND - Socket is ready to send data and Send buffer contains data to send
	def handleSEND(self, name, event):
		try:
			sent = self.client.sock.send(self.net.sbuff)
			self.net.sbuff = self.net.sbuff[sent:]
		except socket.error as error:
			#TODO: Do something here?
			pass

	#SOCKET_ERR - Socket Error has occured
	def handleERR(self, name, event):
		if self.client.sock_quit and not self.client.kill:
			print("Socket Error has occured, stopping...")
			self.client.kill = True
		self.net.reset()

	#SOCKET_HUP - Socket has hung up
	def handleHUP(self, name, event):
		if self.client.sock_quit and not self.client.kill:
			print("Socket has hung up, stopping...")
			self.client.kill = True
		self.net.reset()