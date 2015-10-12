"""
RespawnPlugin's scope is huge, only KeepAlivePlugin does more
"""

import logging

from spockbot.mcdata import constants
from spockbot.plugins.base import PluginBase

logger = logging.getLogger('spockbot')


class RespawnPlugin(PluginBase):
    requires = ('Net', 'ClientInfo')
    events = {
        'client_death': 'handle_death'
    }

    # You be dead
    def handle_death(self, name, data):
        self.net.push_packet(
            'PLAY>Client Status', {'action': constants.CL_STATUS_RESPAWN}
        )
