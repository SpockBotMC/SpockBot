from data_types import *

extensions = {}
def extension(ident):
	def inner(cl):
		extensions[ident] = cl
		return cl
	return inner

@extension(0x17)
class Extension17:
	@classmethod
	def decode_extra(self, packet, bbuff):
		if packet.data['thrower_entity_id'] > 0:
			packet.data['x2'] = unpack(bbuff, 'short')
			packet.data['y2'] = unpack(bbuff, 'short')
			packet.data['z2'] = unpack(bbuff, 'short')
	
	@classmethod
	def encode_extra(self, packet):
		append = ''
		if packet.data['thrower_entity_id'] > 0:
			for i in ('x2','y2','z2'):
				append += pack('short', packet.data[i])
		return append

@extension(0x33)
class Extension33:
	@classmethod
	def decode_extra(self, packet, bbuff):
		packet.data['data'] = unpack_array_fast(bbuff, 'ubyte', packet.data['data_size'])
		del packet.data["data_size"]
	
	@classmethod
	def encode_extra(self, packet):
		packet.data['data_size'] = len(packet.data['data'])
		return pack_array_fast('ubyte', packet.data['data'])

@extension(0x34)
class Extension34:
	@classmethod
	def decode_extra(self, packet, bbuff):
		packet.data["blocks"] = []
		for i in range(packet.data['record_count']):
			data = unpack(bbuff, 'uint')
			block = {
				'metadata': (data	 )   & 0xF,
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

@extension(0x3C)
class Extension3C:
	@classmethod
	def decode_extra(self, packet, bbuff):
		records = unpack_array_fast(bbuff, 'byte', packet.data['data_size']*3)
		i = 0
		packet.data["blocks"] = []
		while i < packet.data['data_size']*3:
			packet.data["blocks"].append(dict(zip(('x','y','z'), records[i:i+3])))
			i+=3
		del packet.data["data_size"]
	
	@classmethod
	def encode_extra(self, packet):
		packet.data['data_size'] = len(packet.data['blocks'])
		array = []
		for i in packet.data['blocks']:
			array += [i['x'], i['y'], i['z']]
		
		return pack_array_fast('byte', array)

@extension(0x68)
class Extension68:
	@classmethod
	def decode_extra(self, packet, bbuff):
		packet.data["slots_data"] = unpack_array(bbuff, 'slot', packet.data["data_size"])
		del packet.data["data_size"]
	
	@classmethod
	def encode_extra(self, packet):
		packet.data['data_size'] = len(packet.data['slots_data'])
		return pack_array('slot', packet.data['slots_data'])

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
class Extension83:
	@classmethod
	def decode_extra(self, packet, bbuff):
		packet.data["data"] = unpack_array_fast(bbuff, 'ubyte', packet.data['data_size'])
		del packet.data["data_size"]
	
	@classmethod
	def encode_extra(self, packet):
		packet.data['data_size'] = len(packet.data['data'])
		return pack_array_fast('ubyte', packet.data['data'])

@extension(0xFA)	
class ExtensionFA:
	@classmethod
	def decode_extra(self, packet, bbuff):
		packet.data["data"] = unpack_array_fast(bbuff, 'byte', packet.data['data_size'])
		del packet.data["data_size"]
	
	@classmethod
	def encode_extra(self, packet):
		packet.data['data_size'] = len(packet.data['data'])
		return pack_array_fast('byte', packet.data['data'])
