import select
from spock.net.clients import baseclient

rmask = select.POLLIN|select.POLLERR|select.POLLHUP
smask = select.POLLOUT|select.POLLIN|select.POLLERR|select.POLLHUP

class PollClient(baseclient.BaseClient):
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.poll = select.poll()
		self.poll.register(self.sock, smask)

	def get_flags(self):
		flags = []
		if self.send:
			self.poll.register(self.sock, smask)
			self.send = False
		else:
			self.poll.register(self.sock, rmask)
		try:
			poll = self.poll.poll(self.get_timeout())
		except select.error as e:
			print(str(e))
			poll = []
		if poll:
			poll = poll[0][1]
			if poll&select.POLLERR: flags.append('SOCKET_ERR')
			if poll&select.POLLHUP: flags.append('SOCKET_HUP')
			if poll&select.POLLIN:  flags.append('SOCKET_RECV')
			if poll&select.POLLOUT: flags.append('SOCKET_SEND')
		if self.auth_err:           flags.append('AUTH_ERR'); self.auth_err = False
		if self.sess_err:           flags.append('SESS_ERR'); self.sess_err = False
		return flags

	def reset(self):
		self.poll.unregister(self.sock)
		self.sock.close()
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.setblocking(0)
		self.poll.register(self.sock)