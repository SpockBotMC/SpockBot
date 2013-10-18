import urllib.request
import urllib.error
import hashlib
import socket

# This function courtesy of barneygale
def javaHexDigest(digest):
	d = int(digest.hexdigest(), 16)
	if d >> 39 * 4 & 0x8:
		d = "-%x" % ((-d) & (2 ** (40 * 4) - 1))
	else:
		d = "%x" % d
	return d

def HashServerId(serverid, sharedsecret, pubkey):
	sha1 = hashlib.sha1()
	sha1.update(serverid.encode('ascii'))
	sha1.update(sharedsecret)
	sha1.update(pubkey)
	return javaHexDigest(sha1)

def AuthenticateMinecraftSession(username, sessionid, serverid):
	url = "http://session.minecraft.net/game/joinserver.jsp?user=" + username + "&sessionId=" + sessionid + "&serverId=" + serverid
	try:
		return urllib.request.urlopen(url).read().decode('ascii')
	except urllib.error.URLError:
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

#TODO: Support 1.6 Server List Ping
def EncodeSLP(packet):
	pass

def DecodeSLP(packet):
	rstring = packet.data['reason'][3:].split('\x00')
	return {'protocol_version': int(rstring[0]),
		'server_version': rstring[1],
		'motd': rstring[2],
		'players': int(rstring[3]),
		'max_players': int(rstring[4]),
	}