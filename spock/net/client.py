import sys

if sys.platform != 'win32':
	from spock.net.clients.pollclient import PollClient
	Client = PollClient
else:
	from spock.net.clients.baseclient import BaseClient
	Client = BaseClient
