import asyncore
import socket

recv_bufsize = 4096

class AsyncSocket(asyncore.dispatcher):
	def __init__(self, bbuff, pbuff):
		asyncore.dispatcher.__init__(self)
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.bbuff = bbuff
		self.pbuff = pbuff

	def handle_connect(self):
		pass

	def handle_close(self):
		self.close()

	def handle_read(self):
		self.bbuff.append(self.recv(4096))

	def handle_write(self):
