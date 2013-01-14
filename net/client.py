import socket
import asyncore

from spock.mcp import bound_buffer
from spock.mcp.packet import Packet, read_packet 
from spock.net import encryption


class Client(asyncore.dispatcher):
	def __init__(self, **custom_settings):
		self.bbuff = bound_buffer.BoundBuffer()
		self.stream_cipher = encryption.StreamCipher()