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

from spockbot.mcp.yggdrasil import YggdrasilCore
from spockbot.plugins.base import PluginBase, pl_announce

logger = logging.getLogger('spockbot')


# This function courtesy of barneygale
def java_hex_digest(digest):
    d = int(digest.hexdigest(), 16)
    if d >> 39 * 4 & 0x8:
        d = "-%x" % ((-d) & (2 ** (40 * 4) - 1))
    else:
        d = "%x" % d
    return d


class AuthCore(object):
    def __init__(self, event, online_mode, auth_timeout):
        self.online_mode = online_mode
        self.auth_timeout = auth_timeout
        self.__event = event
        self.ygg = YggdrasilCore()
        self._shared_secret = None
        self._username = None

    def get_username(self):
        return self._username

    def set_username(self, username):
        self.ygg.username = username

    username = property(get_username, set_username)

    def set_password(self, password):
        if password and not self.online_mode:
            logger.warning("PASSWORD PROVIDED WITH ONLINE_MODE == FALSE")
            logger.warning("YOU PROBABLY DIDN'T WANT TO DO THAT")
        self.ygg.password = password

    password = property(lambda x: bool(x.ygg.password), set_password)

    def set_client_token(self, client_token):
        if not self.online_mode:
            logger.warning("CLIENT TOKEN PROVIDED WITH ONLINE_MODE == FALSE")
            logger.warning("YOU PROBABLY DIDN'T WANT TO DO THAT")
        self.ygg.client_token = client_token

    client_token = property(
        lambda x: bool(x.ygg.client_token), set_client_token
    )

    def set_auth_token(self, auth_token):
        if not self.online_mode:
            logger.warning("AUTH TOKEN PROVIDED WITH ONLINE_MODE == FALSE")
            logger.warning("YOU PROBABLY DIDN'T WANT TO DO THAT")
        self.ygg.auth_token = auth_token

    auth_token = property(
        lambda x: bool(x.ygg.auth_token), set_auth_token
    )

    def get_shared_secret(self):
        self._shared_secret = self._shared_secret or os.urandom(16)
        return self._shared_secret

    shared_secret = property(get_shared_secret)

    def start_session(self):
        if not self.online_mode:
            self._username = self.ygg.username
            return True
        if self.ygg.login():
            self._username = self.ygg.selected_profile['name']
            return True
        self.__event.emit('auth_session_error')
        return False

    def send_session_auth(self, pubkey_raw, server_id_raw):
        server_id = java_hex_digest(hashlib.sha1(
            server_id_raw.encode('ascii') + self.shared_secret + pubkey_raw
        ))
        logger.info('Attempting to authenticate with Mojang session server')
        url = "https://sessionserver.mojang.com/session/minecraft/join"
        data = json.dumps({
            'accessToken': self.ygg.access_token,
            'selectedProfile': self.ygg.selected_profile,
            'serverId': server_id,
        }).encode('utf-8')
        headers = {'Content-Type': 'application/json'}
        req = request.Request(url, data, headers)
        try:
            rep = request.urlopen(
                req, timeout=self.auth_timeout
            ).read().decode('ascii')
        except URLError:
            rep = "Couldn't connect to sessionserver.mojang.com"
        if rep:
            logger.warning('Mojang session auth response: %s', rep)
        logger.info('Session authentication successful')


@pl_announce('Auth')
class AuthPlugin(PluginBase):
    requires = 'Event'
    defaults = {
        'online_mode': True,
        'auth_timeout': 3,  # No idea how long this should be, 3s seems good
        'auth_quit': True,
        'sess_quit': True,
    }
    events = {
        'auth_login_error': 'handle_auth_error',
        'auth_session_error': 'handle_session_error',
    }

    def __init__(self, ploader, settings):
        super(AuthPlugin, self).__init__(ploader, settings)
        self.sess_quit = self.settings['sess_quit']
        self.auth_quit = self.settings['auth_quit']
        ploader.provides('Auth', AuthCore(
            self.event,
            self.settings['online_mode'],
            self.settings['auth_timeout']
        ))

    def handle_auth_error(self, name, data):
        if self.auth_quit:
            logger.error('AUTH: Session authentication error, calling kill')
            self.event.kill()

    def handle_session_error(self, name, data):
        if self.sess_quit:
            logger.error('AUTH: Session start error, calling kill')
            self.event.kill()
