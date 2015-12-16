"""
This plugin creates a convenient start() method and attaches it directly
to the client. More complex bots will likely want to create their own
initialization plugin, so StartPlugin stays out of the way unless you
call the start() method. However, the start() method is very convenient
for demos and tutorials, and illustrates the basic steps for initializing
a bot.
"""

from spockbot.plugins.base import PluginBase


class StartPlugin(PluginBase):
    requires = ('Auth', 'Event', 'Net')
    events = {
        'event_start': 'start_session_and_connect',
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
        self.host = host or self.settings['host']
        self.port = port or self.settings['port']
        self.auth.username = self.settings['username']
        self.auth.password = self.settings['password']
        self.event.event_loop()

    def start_session_and_connect(self, _, __):
        if self.auth.start_session():
            self.net.connect(self.host, self.port)
