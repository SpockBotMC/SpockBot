import asyncore
import socket

recv_bufsize = 4096

class AsyncSocket(asyncore.dispatcher):
	def __init__(self):
		asyncore.dispatcher.__init__(self)
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sbuff = ''
		self.rbuff = ''

	def read_buff(self):
		buff = self.rbuff
		self.rbuff = ''
		return buff

	def write_buff(self, buff):
		self.sbuff += buff

	def handle_connect(self):
		pass

	def handle_close(self):
		pass

	def handle_read(self):
		self.rbuff += self.recv(recv_bufsize)

	def handle_write(self):
		if self.sbuff:
			sent = self.send(self.sbuff)
			self.sbuff = self.sbuff[sent:]

class CryptoAsyncSocket(AsyncSocket):
	def __init__(self, cipher = None):
		AsyncSocket.__init__(self)
		self.cipher = cipher
		self.encypted = (True if cipher else False)
		self.cbuff = ''

	def enable_crypto(self, cipher):
		self.cipher = cipher
		self.encypted = True

	def disable_crypto(self):
		self.cipher = None
		self.encypted = False

	def handle_read(self):
		if self.encypted:
			self.rbuff += self.cipher.decrypt(self.recv(recv_bufsize))
		else:
			self.rbuff += self.recv(recv_bufsize)

	def handle_write(self):
		if self.encypted:
			if not self.cbuff and self.sbuff:
				self.cbuff = self.cipher.encrypt(self.sbuff)
				self.sbuff = ''
			if self.cbuff:
				sent = self.send(self.cbuff)
				self.cbuff = self.cbuff[sent:]
		elif self.sbuff:
			sent = self.send(self.sbuff)
			self.sbuff = self.sbuff[sent:]