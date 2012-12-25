import socket
import time
import struct
import types

username = "nickelpro"

def ByteToHex( byteStr ):
	"""
	Convert a byte string to it's hex string representation e.g. for output.
	"""
	
	# Uses list comprehension which is a fractionally faster implementation than
	# the alternative, more readable, implementation below
	#   
	#	hex = []
	#	for aChar in byteStr:
	#		hex.append( "%02X " % ord( aChar ) )
	#
	#	return ''.join( hex ).strip()		

	return ''.join( [ "%02X " % ord( x ) for x in byteStr ] ).strip()


def sendString(socket, value):
	if (type(value) is not types.StringType):
		value = str(value)
	socket.send(struct.pack('>h', value.__len__()))
	socket.send(value.encode('utf-16be')) 

def sendInt(socket, value):
	assert type(value) is types.IntType, "value is not an integer: %r" % value
	socket.send(struct.pack('>i', value))

def sendByte(socket, value):
	socket.send(struct.pack('>b', value))

def test(host='localhost', port=25565):
	#Set up our socket
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((host, port))
	s.send('\x02')
	sendByte(s, 49)
	sendString(s, username)
	sendString(s, host)
	sendInt(s, port)
	login_packet = s.recv(1024)
	print ByteToHex(login_packet)

test(host='untamedears.com')