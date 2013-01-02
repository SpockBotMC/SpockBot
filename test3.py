from mcp import mcdata
from packethandler import DecodeData

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

byte_array = '\x00\x03\x01\x02\x03'

print ByteToHex(DecodeData(byte_array, 'ubyte')[1])