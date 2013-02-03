from spock.net.client import Client
from login import username, password

client = Client()
client.login(username, password, 'localhost')