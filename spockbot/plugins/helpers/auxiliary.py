"""
Auxilliary Plugin does the things that other plugins don't want to do.
Keep Alives, Handshaking, Respawning, and that one encryption packet all
get to live here because they don't really belong other places.
All functionality is configurable.
"""

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding

from spockbot.mcdata import constants
from spockbot.mcp import proto
from spockbot.plugins.base import PluginBase


backend = default_backend()


class AuxiliaryPlugin(PluginBase):
    requires = 'Auth', 'Net'
    defaults = {
        'Encryption': True,
        'Handshake': True,
        'KeepAlive': True,
        'Respawn': True,
    }
    settings_map = {
        'Encryption': ('LOGIN<Encryption Request', 'handle_encrypt_request'),
        'Handshake': ('net_connect', 'handshake_and_login_start'),
        'KeepAlive': ('PLAY<Keep Alive', 'handle_keep_alive'),
        'Respawn': ('client_death', 'handle_death'),
    }

    def __init__(self, ploader, settings):
        super(AuxiliaryPlugin, self).__init__(ploader, settings)
        for key, val in self.settings.items():
            if val:
                event, attr = self.settings_map[key]
                ploader.reg_event_handler(event, getattr(self, attr))

    def handshake_and_login_start(self, _, __):
        self.net.push_packet('HANDSHAKE>Handshake', {
            'protocol_version': proto.MC_PROTOCOL_VERSION,
            'host': self.net.host,
            'port': self.net.port,
            'next_state': proto.LOGIN_STATE,
        })
        self.net.push_packet('LOGIN>Login Start', {'name': self.auth.username})

    # Encryption Key Request - Request for client to start encryption
    def handle_encrypt_request(self, name, packet):
        pubkey_raw = packet.data['public_key']
        if self.auth.online_mode:
            self.auth.send_session_auth(pubkey_raw, packet.data['server_id'])
        pubkey = serialization.load_der_public_key(pubkey_raw, backend)
        encrypt = lambda data: pubkey.encrypt(data, padding.PKCS1v15())  # flake8: noqa
        self.net.push_packet('LOGIN>Encryption Response', {
            'shared_secret': encrypt(self.auth.shared_secret),
            'verify_token': encrypt(packet.data['verify_token']),
        })
        self.net.enable_crypto(self.auth.shared_secret)

    # Keep Alive - Reflects data back to server
    def handle_keep_alive(self, name, packet):
        packet.new_ident('PLAY>Keep Alive')
        self.net.push(packet)

    # You be dead
    def handle_death(self, name, data):
        self.net.push_packet('PLAY>Client Status',
                             {'action': constants.CL_STATUS_RESPAWN})
