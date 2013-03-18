import psycopg2
from copy import copy
from skylogin import dbname, dbuser, dbpass
from spock.net.cflags import cflags

class SkyNetPlugin:
	def __init__(self, client):
		self.client = client
		self.player_list = {}

		client.register_dispatch(self.record_event, 0xC9)
		client.register_dispatch(self.log_off, 0xFF)
		client.register_handler(self.log_off, cflags['SOCKET_ERR'], cflags['SOCKET_HUP'], cflags['KILL_EVENT'])

		self.conn = psycopg2.connect(database = dbname, user = dbuser, password = dbpass)
		self.cur = self.conn.cursor()
		self.cur.execute("SET timezone = 'UTC';")
		self.conn.commit()

	def record_event(self, packet):
		self.cur.execute("""INSERT INTO skynet_events (player_name, online, time) 
			VALUES (%s, %s, NOW());""", (packet.data['player_name'], packet.data['online'],))
		self.conn.commit()
		self.player_list = copy(self.client.playerlist)

	def log_off(self, *args):
		for player in self.player_list:
			self.cur.execute("""INSERT INTO skynet_events (player_name, online, time)
				VALUES (%s, False, NOW());""", (player,))
			self.conn.commit()
		self.player_list = {}
