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

from mcp.packet import Packet, read_packet
from mcp.bound_buffer import BoundBuffer
from mcp import utils
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
	bbuff = BoundBuffer()
	s.send(Packet(ident = 02, data = {
		'protocol_version': 51,
		'username': username,
		'server_host': host,
		'server_port': port,
		}).encode()
	)
	bbuff.append(s.recv(4096))
	packet = read_packet(bbuff)
	pubkey = RSA.importKey(packet.data['public_key'])
	sharedSecret = _UserFriendlyRNG.get_random_bytes(16)
	sha1 = hashlib.sha1()
	sha1.update(packet.data['server_id'])
	sha1.update(sharedSecret)
	sha1.update(packet.data['public_key'])
	serverid = utils.javaHexDigest(sha1)
	url = "http://session.minecraft.net/game/joinserver.jsp?user=" + username + "&sessionId=" + sessionid + "&serverId=" + serverid
	response = urllib2.urlopen(url).read()
	print response
	RSACipher = PKCS1_v1_5.new(pubkey)
	encryptedSanityToken = RSACipher.encrypt(str(packet.data['verify_token']))
	encryptedSharedSecret = RSACipher.encrypt(str(sharedSecret))
	s.send(Packet(ident = 0xFC, data = {
		'shared_secret_length': encryptedSharedSecret.__len__(),
		'shared_secret': encryptedSharedSecret,
		'verify_token_length': encryptedSanityToken.__len__(),
		'verify_token': encryptedSanityToken
		}).encode()
	)

	blarg = s.recv(4096)
	print utils.ByteToHex(blarg)


test(username, password, host='192.168.1.108')