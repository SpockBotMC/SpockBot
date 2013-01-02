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

from mcp import utils, packet, bound_buffer
from login import username, password

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
	data = {
		'protocol_version': 49,
		'username': username,
		'server_host': host,
		'server_port': port,
	}
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