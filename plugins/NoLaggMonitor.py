import threading
import re
import psycopg2
from skylogin import dbname, dbuser, dbpass
from spock.mcp.mcpacket import Packet
from spock.net.cflags import cflags
from spock.net.timer import ThreadedTimer

class NoLaggPlugin:
	def __init__(self, client):
		self.client = client
		self.packet = Packet(ident = 0x03, data = {
			"text": "/nolagg stats"
			})
		self.stop_event = threading.Event()
		client.register_dispatch(self.start_timer, 0x01)
		client.register_handler(self.stop_timer, cflags['SOCKET_ERR'], cflags['SOCKET_HUP'], cflags['KILL_EVENT'])
		client.register_dispatch(self.stop_timer, 0xFF)

		self.conn = psycopg2.connect(database = dbname, user = dbuser, password = dbpass)
		self.cur = self.conn.cursor()
		self.cur.execute("SET timezone = 'UTC';")
		self.conn.commit()

	def start_timer(self, *args):
		ThreadedTimer(self.stop_event, 300, self.check_nolagg, -1).start()

	def stop_timer(self, *args):
		self.stop_event.set()
		self.stop_event = threading.Event()

	#Never ever, ever, do what I'm about to do
	#This is a very special case
	def check_nolagg(self, *args):
		self.client.push(self.packet)
		if self.handle_memory not in self.client.plugin_dispatch[0x03]:
			self.client.register_dispatch(self.handle_memory, 0x03)

	def handle_memory(self, packet):
		self.toreturn = {}
		msg = re.sub('\xa7.', '', packet.data['text'])
		match = re.match('Memory: \|* ([0-9]+)/([0-9]+) ([A-Z]+)', msg)
		if match:
			matchlist = match.groups()
			self.toreturn['UsedMem'] = int(matchlist[0])
			self.toreturn['TotalMem'] = int(matchlist[1])
			self.toreturn['MemUnit'] = matchlist[2]

			#Remove this function from the dispatch list and put the next one on
			self.client.plugin_dispatch[0x03].remove(self.handle_memory)
			self.client.register_dispatch(self.handle_ticks, 0x03)

	def handle_ticks(self, packet):
		msg = re.sub('\xa7.', '', packet.data['text'])
		match = re.match('Ticks per second: ([0-9]+\.[0-9]+) \[([0-9]+\.[0-9]+)\%\]', msg)
		if match:
			matchlist = match.groups()
			self.toreturn['Tps'] = float(matchlist[0])
			self.toreturn['PercentTps'] = float(matchlist[1])

			self.client.plugin_dispatch[0x03].remove(self.handle_ticks)
			self.client.register_dispatch(self.handle_chunks, 0x03)

	def handle_chunks(self, packet):
		msg = re.sub('\xa7.', '', packet.data['text'])
		match = re.match('Chunks: ([0-9]+) \[([0-9]+) U\](?: \[[\+|\-][0-9]+\]){3} \[([0-9]+) lighting\]', msg)
		if match:
			matchlist = match.groups()
			self.toreturn['LoadedChunks'] = int(matchlist[0])
			self.toreturn['LoadedUChunks'] = int(matchlist[1])
			self.toreturn['LightingChunks'] = int(matchlist[2])

			self.client.plugin_dispatch[0x03].remove(self.handle_chunks)
			self.client.register_dispatch(self.handle_entities, 0x03)

	def handle_entities(self, packet):
		msg = re.sub('\xa7.', '', packet.data['text'])
		match = re.match('Entities: ([0-9]+)(?: \[([0-9]+) [A-Za-z]+\])(?: \[([0-9]+) [A-Za-z]+\])(?: \[([0-9]+) [A-Za-z]+\])(?: \[([0-9]+) [A-Za-z]+\])', msg)
		if match:
			matchlist = match.groups()
			self.toreturn['TotalEntities'] = int(matchlist[0])
			self.toreturn['Mobs'] = int(matchlist[1])
			self.toreturn['Items'] = int(matchlist[2])
			self.toreturn['TNT'] = int(matchlist[3])
			self.toreturn['Players'] = int(matchlist[4])

			self.client.plugin_dispatch[0x03].remove(self.handle_entities)
			self.client.register_dispatch(self.handle_compress, 0x03)

	def handle_compress(self, packet):
		msg = re.sub('\xa7.', '', packet.data['text'])
		match = re.match('Packet compression busy: ([0-9]+\.[0-9]+)\% busy', msg)
		if match:
			matchlist = match.groups()
			self.toreturn['PacketCompr'] = float(matchlist[0])

			self.client.plugin_dispatch[0x03].remove(self.handle_compress)
			self.record_stats()

	#SQL to log stats will go here
	def record_stats(self):
		self.cur.execute("""INSERT INTO skynet_stats ("Time", "UsedMem", "TotalMem", "MemUnit", "Tps", "PercentTps", 
		"LoadedChunks", "LoadedUChunks", "LightingChunks", "TotalEntities", "Mobs", "Items", "TNT", "Players", "PacketCompr") 
		VALUES (NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);""", (
			self.toreturn['UsedMem'], self.toreturn['TotalMem'], self.toreturn['MemUnit'],
			self.toreturn['Tps'], self.toreturn['PercentTps'],
			self.toreturn['LoadedChunks'], self.toreturn['LoadedUChunks'], self.toreturn['LightingChunks'],
			self.toreturn['TotalEntities'], self.toreturn['Mobs'], self.toreturn['Items'], self.toreturn['TNT'], self.toreturn['Players'],
			self.toreturn['PacketCompr'],
			)
		)
		self.conn.commit()
		self.toreturn = {}