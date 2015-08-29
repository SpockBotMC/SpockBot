"""
Registers timers to provide the necessary tick rates expected by MC servers
"""
from spock.mcdata.constants import CLIENT_TICK_RATE
from spock.plugins.base import PluginBase


class TickerPlugin(PluginBase):
    requires = ('Event', 'Timers')
    events = {
        'PLAY_STATE': 'start_tickers',
    }

    def start_tickers(self, _, __):
        self.timers.reg_event_timer(CLIENT_TICK_RATE, self.client_tick)

    def client_tick(self):
        self.event.emit('action_tick')
        self.event.emit('physics_tick')
        self.event.emit('client_tick')
