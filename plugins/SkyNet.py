import psycopg2
from skylogin import dbname, dbuser, dbpass

class SkyNetPlugin:
	def __init__(self, client):
		self.conn = psycopg2.connect(database = dbname, user = dbuser, password = dbpass)
		self.cur = self.conn.cursor()
		self.cur.execute("SET timezone = 'UTC';")

		self.client = client
		client.register_dispatch(self.record_event, 0xC9)

	def record_event(self, packet):
		self.cur.execute("""INSERT INTO skynet_events (player_name, online, time) 
			VALUES (%s, %s, NOW());""", (packet.data['player_name'], packet.data['online'],))
		self.conn.commit()
