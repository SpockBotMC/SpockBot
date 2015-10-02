"""
This plugin creates a convenient start() method and attaches it directly
to the client. More complex bots will likely want to create their own
initialization plugin, so StartPlugin stays out of the way unless you
call the start() method. However, the start() method is very convenient
for demos and tutorials, and illustrates the basic steps for initializing
a bot.
"""

from spock.mcp import mcdata
from spock.plugins.base import PluginBase


class StartPlugin(PluginBase):
    requires = ('Event', 'Net', 'Auth')
    events = {
        'event_start': 'start_session',
        'connect': 'handshake_and_login_start',
    }
    defaults = {
        'username': 'Bot',
        'password': None,
        'host': 'localhost',
        'port': 25565,
    }

    def __init__(self, ploader, settings):
        super(StartPlugin, self).__init__(ploader, settings)
        setattr(ploader, 'start', self.start)

    def start(self, host=None, port=None):
        self.host = host if host else self.settings['host']
        self.port = port if port else self.settings['port']
        self.event.event_loop()

    def start_session(self, _, __):
        if 'error' not in self.auth.start_session(
                self.settings['username'],
                self.settings['password']
        ):
            self.net.connect(self.host, self.port)

    def handshake_and_login_start(self, _, __):
        self.net.push_packet('HANDSHAKE>Handshake', {
            'protocol_version': mcdata.MC_PROTOCOL_VERSION,
            'host': self.net.host,
            'port': self.net.port,
            'next_state': mcdata.LOGIN_STATE
        })
        self.net.push_packet('LOGIN>Login Start', {'name': self.auth.username})
