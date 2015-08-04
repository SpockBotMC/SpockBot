"""
This plugin creates a convenient start() method and attaches it directly
to the client. More complex bots will likely want to create their own
initialization plugin, so StartPlugin stays out of the way unless you
call the start() method. However, the start() method is very convenient
for demos and tutorials, and illustrates the basic steps for initializing
a bot.
"""

from spock import utils
from spock.mcp import mcpacket, mcdata
from spock.plugins.base import PluginBase

class StartPlugin(PluginBase):
    requires = ('Event', 'Net', 'Auth')
    defaults = {
        'username': 'Bot',
        'password': None,
        'host': 'localhost',
        'port': 25565,
    }
    def __init__(self, ploader, settings):
        super(self.__class__, self).__init__(ploader, settings)
        setattr(ploader, 'start', self.start)

    def start(self, host = None, port = None):
        if 'error' not in self.auth.start_session(
            self.settings['username'],
            self.settings['password']
        ):
            host = host if host else self.settings['host']
            port = port if port else self.settings['port']
            self.net.connect(host, port)
            self.handshake()
            self.login_start()
            self.event.event_loop()

    def handshake(self):
        self.net.push_packet('HANDSHAKE>Handshake', {
            'protocol_version': mcdata.MC_PROTOCOL_VERSION,
            'host': self.net.host,
            'port': self.net.port,
            'next_state': mcdata.LOGIN_STATE
        })

    def login_start(self):
        self.net.push_packet('LOGIN>Login Start', {'name': self.auth.username})
