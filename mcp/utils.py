import re
import urllib2
import urllib

from hashlib import sha1

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

def DecodeServerListPing(packet):
	rstring = packet.data['reason'][3:].split('\x00')
	return {'protocol_version': int(rstring[0]),
		'server_version': rstring[1],
		'motd': rstring[2],
		'players': int(rstring[3]),
		'max_players': int(rstring[4])
	}