"""
Provides authorization functions for Mojang's login and session servers
"""

import hashlib
import json
import logging
import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from spock.mcp.yggdrasil import YggdrasilCore
from spock.plugins.base import PluginBase
from spock.utils import pl_announce

try:
    import urllib.request as request
    from urllib.error import URLError
except ImportError:
    import urllib2 as request
    from urllib2 import URLError

logger = logging.getLogger('spock')
backend = default_backend()


# This function courtesy of barneygale
def java_hex_digest(digest):
    d = int(digest.hexdigest(), 16)
    if d >> 39 * 4 & 0x8:
        d = "-%x" % ((-d) & (2 ** (40 * 4) - 1))
    else:
        d = "%x" % d
    return d


@pl_announce('Auth')
class AuthPlugin(PluginBase):
    requires = ('Event', 'Net')
    defaults = {
        'online_mode': False,
        'sess_quit': True,
    }
    events = {
        'AUTH_ERR': 'handle_auth_error',
        'SESS_ERR': 'handle_session_error',
        'LOGIN<Encryption Request': 'handle_encryption_request',
    }

    def __init__(self, ploader, settings):
        super(AuthPlugin, self).__init__(ploader, settings)
        self.online_mode = self.settings['online_mode']
        self.sess_quit = self.settings['sess_quit']
        self.ygg = YggdrasilCore()
        self._shared_secret = None
        self._username = None
        ploader.provides('Auth', self)

    def get_username(self):
        return self._username

    def set_username(self, username):
        self.ygg.username = username

    username = property(get_username, set_username)

    def set_password(self, password):
        self.ygg.password = password

    password = property(lambda x: bool(x.ygg.password), set_password)

    def start_session(self):
        if not self.online_mode:
            self._username = self.ygg.username
            return True
        if self.ygg.login():
            self._username = self.ygg.selected_profile['name']
            return True
        self.event.emit('AUTH_ERR')
        return False

    def get_shared_secret(self):
        self._shared_secret = self._shared_secret or os.urandom(16)
        return self._shared_secret

    shared_secret = property(get_shared_secret)

    def handle_auth_error(self, name, data):
        self.event.kill()

    def handle_session_error(self, name, data):
        if self.sess_quit:
            self.event.kill()

    # Encryption Key Request - Request for client to start encryption
    def handle_encryption_request(self, name, packet):
        pubkey_raw = packet.data['public_key']
        if self.online_mode:
            self.send_request_online(packet)
        logger.warning("Server in offline mode can't request encryption")
        pubkey = serialization.load_der_public_key(pubkey_raw, backend)
        encrypt = lambda data: pubkey.encrypt(data, padding.PKCS1v15())
        self.net.push_packet(
            'LOGIN>Encryption Response',
            {
                'shared_secret': encrypt(self.shared_secret),
                'verify_token': encrypt(packet.data['verify_token']),
            }
        )
        self.net.enable_crypto(self.shared_secret)

    def send_request_online(self, packet):
        pubkey_raw = packet.data['public_key']
        server_id = java_hex_digest(hashlib.sha1(
            packet.data['server_id'].encode('ascii')
            + self.shared_secret
            + pubkey_raw
        ))
        logger.info('Attempting to authenticate session mojang')
        url = "https://sessionserver.mojang.com/session/minecraft/join"
        data = json.dumps({
            'accessToken': self.ygg.access_token,
            'selectedProfile': self.ygg.selected_profile,
            'serverId': server_id,
        }).encode('utf-8')
        headers = {'Content-Type': 'application/json'}
        req = request.Request(url, data, headers)
        try:
            rep = request.urlopen(req).read().decode('ascii')
        except URLError:
            rep = "Couldn't connect to sessionserver.mojang.com"
        if rep:
            logger.warning('Mojang session auth response: %s', rep)
        logger.info('Session authentication successful')
