import socket
import time
import struct
import types
import hashlib
import urllib2
import sys

from Crypto.Random import _UserFriendlyRNG
from Crypto.Util import asn1
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto.Cipher import PKCS1_v1_5

from mcp import utils
from mcp.datautils import DecodeData
from login import username, password

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


class key_request_packet():
	serverid = ""
	public_key = ""
	verify_token = ""

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

def sendShort(socket, value):
	socket.send(struct.pack('>h', value))

def sendFC(socket, secret, token):
	#packet id
	socket.send("\xFC")

	#shared secret
	sendShort(socket, secret.__len__()) #length
	socket.send(secret)

	#token
	sendShort(socket, token.__len__())
	socket.send(token)

def readShort(Bob):
	return struct.unpack('>h', Bob)[0]

def readByteArray(Bob, length):
	return struct.unpack(str(length) + "s", Bob)[0]

def readString(Bob):
	length = readShort(Bob[:2]) * 2
	Bob = Bob[2:]
	return Bob[:length].decode("utf-16be")

def decodeKrPacket(Bob):
	packet = key_request_packet()
	assert Bob[0] == '\xFD'
	Bob = Bob[1:]
	length = readShort(Bob[:2]) * 2
	Bob = Bob[2:]
	packet.serverid = Bob[:length].decode("utf-16be")
	Bob = Bob[length:]
	length = readShort(Bob[:2])
	Bob = Bob[2:]
	packet.public_key = readByteArray(Bob[:length], length)
	Bob = Bob[length:]
	length = readShort(Bob[:2])
	Bob = Bob[2:]
	packet.verify_token = readByteArray(Bob, length)
	return packet




def test(username, password, host='localhost', port=25565):
	#Set up our socket
	loginResponse = utils.LoginToMinecraftNet(username, password)
	if (loginResponse['Response'] != "Good to go!"):
		print "Fuck something broke"
		print loginResponse['Response']
		sys.exit(1)

	username = loginResponse['Username']
	sessionid = loginResponse['SessionID']

	print "Logged in as " + username + "! Your session id is: " + sessionid

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((host, port))
	s.send('\x02')
	sendByte(s, 49)
	sendString(s, username)
	sendString(s, host)
	sendInt(s, port)
	login_packet = s.recv(4096)
	Bob = login_packet
	packet = decodeKrPacket(Bob)
	pubkey = RSA.importKey(packet.public_key)
	sharedSecret = _UserFriendlyRNG.get_random_bytes(16)
	sha1 = hashlib.sha1()
	sha1.update(packet.serverid)
	sha1.update(sharedSecret)
	sha1.update(packet.public_key)
	serverid = utils.javaHexDigest(sha1)
	url = "http://session.minecraft.net/game/joinserver.jsp?user=" + username + "&sessionId=" + sessionid + "&serverId=" + serverid
	response = urllib2.urlopen(url).read()
	print response
	RSACipher = PKCS1_v1_5.new(pubkey)
	encryptedSanityToken = RSACipher.encrypt(str(packet.verify_token))
	encryptedSharedSecret = RSACipher.encrypt(str(sharedSecret))
	sendFC(s, encryptedSharedSecret, encryptedSanityToken)
	blarg = s.recv(4096)
	print ByteToHex(blarg)


test(username, password, host='untamedears.com')