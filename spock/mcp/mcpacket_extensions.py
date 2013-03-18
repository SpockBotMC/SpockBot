from datautils import *
from mcdata import *

extensions = {}
def extension(ident):
	def inner(cl):
		extensions[ident] = cl
		return cl
	return inner

class ArrayExtension:
	data_type = None
	array_name = 'data'
	@classmethod
	def decode_extra(self, packet, bbuff):
		packet.data[self.array_name] = unpack_array(bbuff, self.data_type, packet.data['data_size'])
		del packet.data["data_size"]
	
	@classmethod
	def encode_extra(self, packet):
		packet.data['data_size'] = len(packet.data[self.array_name])
		return pack_array(self.data_type, packet.data[self.array_name])

@extension(0x17)
class Extension17:
	@classmethod
	def decode_extra(self, packet, bbuff):
		if packet.data['object_data'] > 0:
			packet.data['x2'] = unpack(bbuff, 'short')
			packet.data['y2'] = unpack(bbuff, 'short')
			packet.data['z2'] = unpack(bbuff, 'short')
	
	@classmethod
	def encode_extra(self, packet):
		append = ''
		if packet.data['object_data'] > 0:
			for i in ('x2','y2','z2'):
				append += pack('short', packet.data[i])
		return append
	
@extension(0x1D)
class Extension1D(ArrayExtension):
	data_type = 'int'
	array_name = 'entity_ids'
	
@extension(0x33)
class Extension33(ArrayExtension):
	@classmethod
	def decode_extra(self, packet, bbuff):
		packet.data["data"] = bbuff.recv(packet.data['data_size'])

	@classmethod
	def encode_extra(self, packet):
		packet.data['data_size'] = len(packet.data['data'])

@extension(0x34)
class Extension34:
	@classmethod
	def decode_extra(self, packet, bbuff):
		packet.data["blocks"] = []
		for i in range(packet.data['record_count']):
			data = unpack(bbuff, 'uint')
			block = {
				'metadata': (data	 )  & 0xF,
				'type':	 (data >> 4)  & 0xFFF,
				'y':		(data >> 16) & 0xFF,
				'z':		(data >> 24) & 0xF,
				'x':		(data >> 28) & 0xF}
			packet.data["blocks"].append(block)
		del packet.data["data_size"]
	
	@classmethod
	def encode_extra(self, packet):
		packet.data['record_count']  = len(packet.data['blocks'])
		packet.data['data_size'] = 4 * len(packet.data['blocks'])
		append = ''
		for block in packet.data['blocks']:
			append += pack('uint', 
				(block['metadata']  ) +
				(block['type'] <<  4) +
				(block['y']	<< 16) +
				(block['z']	<< 24) +
				(block['x']	<< 28))
		return append

@extension(0x38)
class Extension38:
	@classmethod
	def decode_extra(self, packet, bbuff):
		packet.data["data"] = bbuff.recv(packet.data['data_size'])
		
		packet.data["bitmaps"] = []
		for i in range(packet.data['chunk_column_count']):
			d = {}
			d['x'] = unpack(bbuff, 'int')
			d['z'] = unpack(bbuff, 'int')
			d['primary_bitmap'] = unpack(bbuff, 'short')
			d['secondary_bitmap'] = unpack(bbuff, 'short')
			packet.data["bitmaps"].append(d)
		
		del packet.data["data_size"]
	
	@classmethod
	def encode_extra(self, packet):
		packet.data['data_size'] = len(packet.data['data'])
		
		append = packet.data['data']
		
		for d in packet.data["bitmaps"]:
			append += pack('int', d['x'])
			append += pack('int', d['z'])
			append += pack('short', d['primary_bitmap'])
			append += pack('short', d['secondary_bitmap'])
		
		return append

@extension(0x3C)
class Extension3C:
	@classmethod
	def decode_extra(self, packet, bbuff):
		records = unpack_array(bbuff, 'byte', packet.data['record_count']*3)
		i = 0
		packet.data["blocks"] = []
		while i < packet.data['record_count']*3:
			packet.data["blocks"].append(dict(zip(('x','y','z'), records[i:i+3])))
			i+=3
		
		del packet.data["record_count"]
		
		for i in range(3):
			packet.data["offset_%d" % i] = unpack(bbuff, 'float')
		
	
	@classmethod
	def encode_extra(self, packet):
		packet.data['record_count'] = len(packet.data['blocks'])
		array = []
		for i in packet.data['blocks']:
			array += [i['x'], i['y'], i['z']]
		
		append = pack_array('byte', array)
		for i in range(3):
			append += pack('byte', d['offset_%d' % i])
		
		return append
		
@extension(0x68)
class Extension68(ArrayExtension):
	data_type = 'slot'

@extension(0x82)
class Extension82:
	@classmethod
	def decode_extra(self, packet, bbuff):
		packet.data["text"] = []
		for i in range(4):
			packet.data["text"].append(packet.data.pop("line_%s" % (i+1)))
	
	@classmethod
	def encode_extra(self, packet):
		for i in range(4):
			packet.data["line_%s" % (i+1)] = packet.data["text"][i]
		del packet.data["text"]
		return ''

@extension(0x83)
class Extension83(ArrayExtension):
	data_type = 'ubyte'

@extension(0x84)
class Extension84(ArrayExtension):
	data_type = 'ubyte'
	array_name = 'nbt'

@extension(0xD1)
class ExtensionD1:
	@classmethod
	def decode_extra(self, packet, bbuff):
		if packet.data['mode'] == 0 or packet.data['mode'] == 2:
			packet.data['display_name'] = unpack(bbuff, 'string')
			packet.data['team_prefix'] = unpack(bbuff, 'string')
			packet.data['team_suffix'] = unpack(bbuff, 'string')
		if packet.data['mode'] == 0 or packet.data['mode'] == 3 or packet.data['mode'] == 4:
			packet.data['player_count'] = count = unpack(bbuff, 'short')
			packet.data['players'] = []
			for i in xrange(count):
				packet.data['players'].append(unpack(bbuff, 'string'))

@extension(0xFA)	
class ExtensionFA(ArrayExtension):
	data_type = 'byte'

@extension(0xFC)
class ExtensionFC:
	@classmethod
	def decode_extra(self, packet, bbuff):
		l = unpack(bbuff, 'short')
		packet.data['shared_secret'] = unpack_array(bbuff, 'ubyte', l)
		l = unpack(bbuff, 'short')
		packet.data['verify_token'] = unpack_array(bbuff, 'ubyte', l)
	
	@classmethod
	def encode_extra(self, packet):
		append = ''
		for k in ('shared_secret', 'verify_token'):
			append += pack('short', len(packet.data[k]))
			append += packet.data[k]
		return append
		
@extension(0xFD)
class ExtensionFD:
	@classmethod
	def decode_extra(self, packet, bbuff):
		length = unpack(bbuff, 'short')
		packet.data['public_key'] = bbuff.recv(length)
		length = unpack(bbuff, 'short')
		packet.data['verify_token'] = bbuff.recv(length)
	
	@classmethod
	def encode_extra(self, packet):
		append = ''
		for k in ('public_key', 'verify_token'):
			append += pack('short', len(packet.data[k]))
			append += pack_array('ubyte', packet.data[k])
		return append