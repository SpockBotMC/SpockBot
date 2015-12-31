"""
Registers timers to provide the necessary tick rates expected by MC servers
"""
from spockbot.mcdata.constants import CLIENT_TICK_RATE
from spockbot.plugins.base import PluginBase


class TickerPlugin(PluginBase):
    requires = ('Event', 'Timers')
    events = {
        'PLAY<Join Game': 'start_tickers',
    }

    def start_tickers(self, _, __):
        self.timers.reg_event_timer(CLIENT_TICK_RATE, self.client_tick)

    def client_tick(self):
        self.event.emit('action_tick')
        self.event.emit('physics_tick')
        self.event.emit('client_tick')
