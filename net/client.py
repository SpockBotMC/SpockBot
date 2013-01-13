import socket
import asynchat

from spock.mcp import bound_buffer
from spock.mcp.packet import Packet, read_packet 
from barneymc.net import encryption


class Client(asynchat.async_chat):
	node = NODE_CLIENT
	stop_packet_loop = False
	connected2 = False
	
	settings = {
		'port': 25565,
		'debug_in': False,
		'debug_out': False}


	handlers = {}

	def __init__(self, **custom_settings):
		self.rbuff = bound_buffer.BoundBuffer()
		self.stream_cipher = encryption.StreamCipher()
		
		self.settings.update(custom_settings)
		
		asynchat.async_chat.__init__(self, sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM))
		self.set_terminator(None)

	def log(self, message):
		print '[DEBUG] %s' % (message.encode("ascii", "ignore"))

	#Start a new connection
	def connect2(self):
		self.close()
		self.set_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
		try:
			self.connect((self.settings['host'], self.settings['port']))
		except:
			self.handle_error()
	
	def send_packet(self, packet):
		packet.direction = self.node
		if self.settings['debug_out']:
			print packet
		data = packet.encode()
		data = self.stream_cipher.encrypt(data, self.node)
		self.push(data)

	def collect_incoming_data(self, data):
		#print "Client collecting..."
		self.connected2 = True
		if len(data) > 0:
			data = self.stream_cipher.decrypt(data, other_node[self.node])
			self.rbuff.append(data)
			self.rbuff.save()
			while len(self.rbuff.buff) and not self.stop_packet_loop:
				try:
					p = read_packet(self.rbuff, other_node[self.node])
					self.rbuff.save()
					if self.settings['debug_in']:
						print p
					
					self.dispatch_packet(p)
			
				except bound_buffer.BufferUnderflowException:
					self.rbuff.revert()
					return
	
	def found_terminator(self):
		pass

	def default_handler(self, packet):
		pass
	
	def reflect(self, packet):
		self.send_packet(packet.clone())
		
	def print_packet(self, packet):
		print packet
	
	def handle_error(self):
		raise
	
	#Dispatch a packet to its handler
	def dispatch_packet(self, p):
		self.handlers.get(p.ident, self.default_handler)(p)