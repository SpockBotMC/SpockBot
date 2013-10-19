try:
	from spock.net.clients.pollclient import PollClient
	Client = PollClient
except Exception:
	from spock.net.clients.baseclient import BaseClient
	Client = BaseClient