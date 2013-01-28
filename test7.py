import select
import socket
import logging

from Crypto.Random import _UserFriendlyRNG
from Crypto.Util import asn1
from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto.Cipher import PKCS1_v1_5

from spock.mcp.packet import Packet, decode_packet, read_packet
from spock.mcp import utils, mcdata, bound_buffer
from login import username, password

def login(username, password):
	bufsize = 4096
	host = 'localhost'
	port = 25565
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.setblocking(0)
	poll = select.poll()
	poll.register(sock)
	sbuff = ''

	LoginResponse = utils.LoginToMinecraftNet(username, password)
	if (LoginResponse['Response'] != "Good to go!"):
		logging.error('Login Unsuccessful, Response: %s', LoginResponse['Response'])
		return
	username = LoginResponse['Username']
	sessionid = LoginResponse['SessionID']
	try:
		sock.connect((host, port))
	except socket.error:
		pass
	while not poll.poll()[0][1]&select.POLLOUT:
		pass
	sent = sock.send(Packet(ident = 02, data = {
			'protocol_version': mcdata.MC_PROTOCOL_VERSION,
			'username': username,
			'host': host,
			'port': port,
			}).encode())

	while not poll.poll()[0][1]&select.POLLIN:
		pass
	packet = decode_packet(sock.recv(bufsize))
	if (packet.ident != 0xFD):
		logging.error('Server responded with incorrect packet after handshake: %s', str(hex(packet.ident)))
		return

	#Stage 2: Authenticate with session.minecraft.net
	pubkey = packet.data['public_key']
	print packet
	SharedSecret = _UserFriendlyRNG.get_random_bytes(16)
	serverid = utils.HashServerId(packet.data['server_id'], SharedSecret, pubkey)
	SessionResponse = utils.AuthenticateMinecraftSession(username, sessionid, serverid)
	if (SessionResponse != 'OK'):
		logging.error('Session Authentication Failed, Response: %s', SessionResponse)
		return

	#Stage 3: Send an Encryption Response
	RSACipher = PKCS1_v1_5.new(RSA.importKey(pubkey))
	encryptedSanityToken = RSACipher.encrypt(str(packet.data['verify_token']))
	encryptedSharedSecret = RSACipher.encrypt(str(SharedSecret))
	while not poll.poll()[0][1]&select.POLLOUT:
		pass
	sock.send(Packet(ident = 0xFC, data = {
		'shared_secret': encryptedSharedSecret,
		'verify_token': encryptedSanityToken,
		}).encode()
	)
	while not poll.poll()[0][1]&select.POLLIN:
		pass
	packet = decode_packet(sock.recv(bufsize))
	if (packet.ident != 0xFC):
		logging.error('Server responded with incorrect packet after encryption response: %s', str(hex(packet.ident)))
		return

	#Stage 4: Enable encryption and send Client Status
	encipher = AES.new(SharedSecret, AES.MODE_CFB, IV=SharedSecret)
	decipher = AES.new(SharedSecret, AES.MODE_CFB, IV=SharedSecret)
	while not poll.poll()[0][1]&select.POLLOUT:
		pass
	sock.send(encipher.encrypt(Packet(ident = 0xCD, data = {
		'payload': 0,
		}).encode())
	)
	while not poll.poll()[0][1]&select.POLLIN:
		pass
	packet = decode_packet(decipher.decrypt(sock.recv(bufsize)))
	if (packet.ident != 0x01):
		logging.error('Server responded with incorrect packet after client status: %s', str(hex(packet.ident)))
		return
	data = bound_buffer.BoundBuffer()
	while True:
		while not poll.poll()[0][1]&select.POLLIN:
			pass
		data.append(decipher.decrypt(sock.recv(bufsize)))
		data.save()
		try:
			packet = read_packet(data)
		except bound_buffer.BufferUnderflowException:
			data.revert()
			pass


login(username, password)