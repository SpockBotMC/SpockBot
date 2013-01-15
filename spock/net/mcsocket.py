import asyncore
import socket

recv_bufsize = 4096

class AsyncSocket(asyncore.dispatcher):
	def __init__(self, rbuff, pqueue):
		asyncore.dispatcher.__init__(self)
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sbuff = ''
		self.rbuff = rbuff
		self.pqueue = pqueue

	def handle_connect(self):
		pass

	def handle_close(self):
		pass

	def handle_read(self):
		self.rbuff.append(self.recv(recv_bufsize))
		self.rbuff.save()

	def handle_write(self):
		if not self.sbuff:
			self.sbuff = self.pqueue.popbytes()
		sent = self.send(self.sbuff)
		self.sbuff = self.sbuff[sent:]


class CryptoAsyncSocket(AsyncSocket):
	def __init__(self, rbuff, pqueue, cipher = None):
		AsyncSocket.__init__(self, rbuff, pqueue)
		self.cipher = cipher
		self.encypted = False

	def enable_crypto():
		self.encypted = True

	def handle_read(self):
		if self.encypted:
			self.rbuff.append(self.cipher.decrypt(self.recv(recv_bufsize)))
		else:
			self.rbuff.append(self.recv(recv_bufsize))
		self.rbuff.save()

	def handle_write():
		if not self.sbuff:
			if self.encypted:
				self.sbuff = self.cipher.decrypt(self.pqueue.popbytes())
			else:
				self.sbuff = self.pqueue.popbytes()
		sent = self.send(self.sbuff)
		self.sbuff = self.sbuff[sent:]