"""
Provides interface for Plugin Channels
"""
import logging

from spockbot.mcp import datautils
from spockbot.plugins.base import PluginBase, pl_announce

logger = logging.getLogger('spockbot')


class ChannelsCore(object):
    def __init__(self, net):
        self.net = net

    def encode(self, structure, data):
        encoded = b''
        for dtype, name in structure:
            encoded += datautils.pack(dtype, data[name])
        return encoded

    def decode(self, structure, data):
        decoded = {}
        for dtype, name in structure:
            decoded[name] = datautils.unpack(dtype, data)
        return decoded

    def send(self, channel, data):
        """Send a plugin channel message"""
        self.net.push_packet("PLAY>Plugin Message",
                             {"channel": channel, "data": data})


@pl_announce('Channels')
class ChannelsPlugin(PluginBase):
    requires = ('Event', 'Net')
    events = {
        'PLAY<Plugin Message': 'handle_plugin_message',
    }

    def __init__(self, ploader, settings):
        super(ChannelsPlugin, self).__init__(ploader, settings)
        self.channels = ChannelsCore(self.net)
        ploader.provides('Channels', self.channels)

    def handle_plugin_message(self, name, packet):
        self.event.emit("pchannel_" + packet.data['channel'],
                        packet.data['data'])
