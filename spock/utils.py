import re
import urllib2
import urllib
import hashlib
import socket
import os
import sys

from spock import smpmap

# This function courtesy of barneygale
def javaHexDigest(digest):
	d = long(digest.hexdigest(), 16)
	if d >> 39 * 4 & 0x8:
		d = "-%x" % ((-d) & (2 ** (40 * 4) - 1))
	else:
		d = "%x" % d
	return d

def LoginToMinecraftNet(username, password):
	try:
		url = 'https://login.minecraft.net'
		header = {'Content-Type': 'application/x-www-form-urlencoded'}
		data = {'user': username,
			'password': password,
			'version': '13'}
		data = urllib.urlencode(data)
		req = urllib2.Request(url, data, header)
		opener = urllib2.build_opener()
		response = opener.open(req, None, 10)
		response = response.read()
	except urllib2.URLError:
		return {'Response': "Can't connect to minecraft.net"}
	if (not "deprecated" in response.lower()):
		return {'Response': response}
	response = response.split(":")
	sessionid = response[3]
	toReturn = {'Response': "Good to go!",
				'Username': response[2],
				'SessionID': sessionid
	}
	return toReturn

def HashServerId(serverid, sharedsecret, pubkey):
	sha1 = hashlib.sha1()
	sha1.update(serverid)
	sha1.update(sharedsecret)
	sha1.update(pubkey)
	return javaHexDigest(sha1)

def AuthenticateMinecraftSession(username, sessionid, serverid):
	url = "http://session.minecraft.net/game/joinserver.jsp?user=" + username + "&sessionId=" + sessionid + "&serverId=" + serverid
	try:
		return urllib2.urlopen(url).read()
	except urllib2.URLError:
		return 'Couldn\'t connect to session.minecraft.net'

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

def DecodeSLP(packet):
	rstring = packet.data['reason'][3:].split('\x00')
	return {'protocol_version': int(rstring[0]),
		'server_version': rstring[1],
		'motd': rstring[2],
		'players': int(rstring[3]),
		'max_players': int(rstring[4]),
	}

def ResetClient(client):
	client.poll.unregister(client.sock)
	client.sock.close()
	client.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	client.sock.setblocking(0)
	client.poll.register(client.sock)

	client.sbuff = ''
	client.rbuff.flush()
	client.encrypted = False

	client.world = smpmap.World()
	client.world_time = {
		'world_age': 0,
		'time_of_day': 0,
	}
	client.position = {
		'x': 0,
		'y': 0,
		'z': 0,
		'stance': 0,
		'yaw': 0,
		'pitch': 0,
		'on_ground': False,
	}
	client.health = {
		'health': 20,
		'food': 20,
		'food_saturation': 5,
	}
	client.playerlist = {}
	client.entitylist = {}
	client.spawn_position = {
		'x': 0,
		'y': 0,
		'z': 0,
	}
	client.login_info = {}

#My ghetto daemon function, does most of the things a good daemon needs to do
#The program itself needs to do things like check for and make a PID file, this 
#just does the actual daemonizing step
def daemonize(defaultdir = '/tmp'):
	try:
		pid = os.fork()
		if pid > 0:
			sys.exit(0)
	except OSError:
		sys.exit(1)

	os.chdir(defaultdir)
	os.setsid()
	os.umask(0)

	try:
		pid = os.fork()
		if pid > 0:
			sys.exit(0)
	except OSError:
		sys.exit(1)

	dev_null = open((os.devnull if hasattr(os, "devnull") else '/dev/null'), 'r+')
	sys.stdin = sys.stdout = sys.stderr = dev_null

	sys.stdout.flush()
	sys.stdin.flush()
	sys.stderr.flush()

	return os.getpid()