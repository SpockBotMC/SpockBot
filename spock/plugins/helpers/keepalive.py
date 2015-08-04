"""
KeepalivePlugin is a pretty cool guy. Eh reflects keep alive packets and doesnt
afraid of anything.
"""

from spock.mcp import mcdata, mcpacket
from spock.plugins.base import PluginBase

class KeepalivePlugin(PluginBase):
    requires = ('Net')
    events = {
        'PLAY<Keep Alive': 'handle_keep_alive',
    }

    #Keep Alive - Reflects data back to server
    def handle_keep_alive(self, name, packet):
        packet.new_ident('PLAY>Keep Alive')
        self.net.push(packet)
