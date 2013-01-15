import asyncore
import socket

bufsize = 4096

class AsyncSocket(asyncore.dispatcher):
	def __init__(self, rbuff, sbuff):
		asyncore.dispatcher.__init__(self)
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sbuff = sbuff
		self.rbuff = rbuff
		self.tempbuff = ''

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

	#TODO: Adapt this code to implicitly work with non-bound buffers
	def handle_write():
		if not self.tempbuff:
			if self.encypted:
				self.tempbuff = self.cipher.encrypt(self.sbuff.buff)
			else:
				self.tempbuff = self.sbuff.buff
			self.sbuff.buff = ''
		sent = self.send(self.tempbuff)
		self.tempbuff = self.tempbuff[sent:]