"""
Provides authorization functions for Mojang's login and session servers
"""

import hashlib
import json
# This is for python2 compatibility
try:
    import urllib.request as request
    from urllib.error import URLError
except ImportError:
    import urllib2 as request
    from urllib2 import URLError
import logging
import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding

from spockbot.mcp import yggdrasil
from spockbot.plugins.base import PluginBase
from spockbot.utils import pl_announce


logger = logging.getLogger('spockbot')
backend = default_backend()


# This function courtesy of barneygale
def java_hex_digest(digest):
    d = int(digest.hexdigest(), 16)
    if d >> 39 * 4 & 0x8:
        d = "-%x" % ((-d) & (2 ** (40 * 4) - 1))
    else:
        d = "%x" % d
    return d


class AuthCore(object):
    def __init__(self, authenticated, event):
        self.event = event
        self.authenticated = authenticated
        self.username = None
        self.selected_profile = None
        self.shared_secret = None
        self.ygg = yggdrasil.YggAuth()

    def start_session(self, username, password=''):
        rep = {}
        if self.authenticated:
            logger.info("AUTHCORE: Attempting login with username: %s",
                        username)
            rep = self.ygg.authenticate(username, password)
            if rep is None or 'error' in rep:
                logger.error('AUTHCORE: Login Unsuccessful, Response: %s', rep)
                self.event.emit('AUTH_ERR')
                return rep
            if 'selectedProfile' in rep:
                self.selected_profile = rep['selectedProfile']
                self.username = rep['selectedProfile']['name']
                logger.info("AUTHCORE: Logged in as: %s", self.username)
                logger.info("AUTHCORE: Selected Profile: %s",
                            self.selected_profile)
            else:
                self.username = username
        else:
            self.username = username
        return rep

    def gen_shared_secret(self):
        self.shared_secret = os.urandom(16)
        return self.shared_secret


@pl_announce('Auth')
class AuthPlugin(PluginBase):
    requires = ('Event', 'Net')
    defaults = {
        'authenticated': True,
        'auth_quit': True,
        'sess_quit': True,
    }
    events = {
        'AUTH_ERR': 'handle_auth_error',
        'SESS_ERR': 'handle_session_error',
        'LOGIN<Encryption Request': 'handle_encryption_request',
    }

    def __init__(self, ploader, settings):
        super(AuthPlugin, self).__init__(ploader, settings)
        self.authenticated = self.settings['authenticated']
        self.auth_quit = self.settings['auth_quit']
        self.sess_quit = self.settings['sess_quit']
        self.auth = AuthCore(self.authenticated, self.event)
        self.auth.gen_shared_secret()
        ploader.provides('Auth', self.auth)

    def handle_auth_error(self, name, data):
        if self.auth_quit:
            self.event.kill()

    def handle_session_error(self, name, data):
        if self.sess_quit:
            self.event.kill()

    # Encryption Key Request - Request for client to start encryption
    def handle_encryption_request(self, name, packet):
        pubkey_raw = packet.data['public_key']
        if self.authenticated:
            serverid = java_hex_digest(hashlib.sha1(
                packet.data['server_id'].encode('ascii') +
                self.auth.shared_secret +
                pubkey_raw
            ))
            logger.info(
                "AUTHPLUGIN: Attempting to authenticate session with "
                "sessionserver.mojang.com")
            url = "https://sessionserver.mojang.com/session/minecraft/join"
            data = json.dumps({
                'accessToken': self.auth.ygg.access_token,
                'selectedProfile': self.auth.selected_profile,
                'serverId': serverid,
            }).encode('utf-8')
            headers = {'Content-Type': 'application/json'}
            req = request.Request(url, data, headers)
            try:
                rep = request.urlopen(req).read().decode('ascii')
            except URLError:
                rep = 'Couldn\'t connect to sessionserver.mojang.com'
            if rep != "":
                logger.warning("AUTHPLUGIN: %s", rep)
                self.event.emit('SESS_ERR')
            else:
                logger.info("AUTHPLUGIN: Session authentication successful")
        pubkey = serialization.load_der_public_key(pubkey_raw, backend)

        def encrypt(data):
            return pubkey.encrypt(data, padding.PKCS1v15())

        self.net.push_packet(
            'LOGIN>Encryption Response',
            {
                'shared_secret': encrypt(self.auth.shared_secret),
                'verify_token': encrypt(packet.data['verify_token']),
            }
        )
        self.net.enable_crypto(self.auth.shared_secret)
