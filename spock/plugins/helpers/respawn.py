"""
RespawnPlugin's scope is huge, only KeepAlivePlugin does more
"""

from spock.mcp import mcdata
from spock.plugins.base import PluginBase

import logging
logger = logging.getLogger('spock')

class RespawnPlugin(PluginBase):
    requires = ('Net', 'ClientInfo')
    events = {
        'cl_death': 'handle_death'
    }

    #You be dead
    def handle_death(self, name, data):
        self.net.push_packet(
            'PLAY>Client Status', {'action': mcdata.CL_STATUS_RESPAWN}
        )
