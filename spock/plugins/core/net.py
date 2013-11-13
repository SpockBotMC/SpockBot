import socket
from spock import utils
from spock.plugins.plutils import pl_announce
from spock.mcp import mcpacket, mcdata
from Crypto.Cipher import AES

class AESCipher:
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
		self.connected = False
		self.encrypted = False
		self.proto_state = mcdata.HANDSHAKE_STATE
		self.sbuff = b''
		self.rbuff = utils.BoundBuffer()

	def connect(self, host = 'localhost', port = 25565):
		self.host = host
		self.port = port
		try:
			print("Attempting to connect to host:", host, "port:", port)
			self.client.sock.connect((self.host, self.port))
			self.connected = True
		except socket.error as error:
			#print("Error on Connect (this is normal):", str(error))
			pass

	def change_state(self, state):
		self.proto_state = state

	def push(self, packet):
		data = packet.encode()
		self.sbuff += (self.cipher.encrypt(data) if self.encrypted else data)
		self.client.emit(packet.ident(), packet)
		self.client.send = True

	def read_packet(self, data = b''):
		self.rbuff.append(self.cipher.decrypt(data) if self.encrypted else data)
		try:
			while True:
				self.rbuff.save()
				packet = mcpacket.Packet(ident = (
					self.proto_state,
					mcdata.SERVER_TO_CLIENT,
				)).decode(self.rbuff)
				self.client.emit(packet.ident(), packet)
		except utils.BufferUnderflowException:
			self.rbuff.revert()

	def enable_crypto(self, secret_key):
		self.cipher = AESCipher(secret_key)
		self.encrypted = True

	def disable_crypto(self):
		self.cipher = None
		self.encrypted = False

	def disconnect(self):
		self.client.sock.close()
		self.reset()

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
		ploader.reg_event_handler(
			(mcdata.HANDSHAKE_STATE, mcdata.CLIENT_TO_SERVER, 0x00),
			self.handle00
		)
		ploader.reg_event_handler(
			(mcdata.LOGIN_STATE, mcdata.SERVER_TO_CLIENT, 0x02),
			self.handle02
		)

	#SOCKET_RECV - Socket is ready to recieve data
	def handleRECV(self, name, event):
		try:
			data = self.client.sock.recv(self.client.bufsize)
			if not data: #Just because we have to support socket.select
				self.client.emit('SOCKET_HUP')
				return
			self.net.read_packet(data)
		except socket.error as error:
			#TODO: Do something here?
			pass

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

	#Handshake - Change to whatever the next state is going to be
	def handle00(self, name, packet):
		self.net.change_state(packet.data['next_state'])

	#Login Success - Change to Play state
	def handle02(self, name, packet):
		self.net.change_state(mcdata.PLAY_STATE)