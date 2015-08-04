"""
Provides authorization functions for Mojang's login and session servers
"""

import hashlib
import json
#This is for python2 compatibility
try:
    import urllib.request as request
    from urllib.error import URLError
except ImportError:
    import urllib2 as request
    from urllib2 import URLError
from Crypto.Cipher import PKCS1_v1_5
from Crypto.PublicKey import RSA
from Crypto import Random
from spock import utils
from spock.mcp import mcdata, mcpacket, yggdrasil
from spock.utils import pl_announce
from spock.plugins.base import PluginBase

import logging
logger = logging.getLogger('spock')

# This function courtesy of barneygale
def JavaHexDigest(digest):
    d = int(digest.hexdigest(), 16)
    if d >> 39 * 4 & 0x8:
        d = "-%x" % ((-d) & (2 ** (40 * 4) - 1))
    else:
        d = "%x" % d
    return d

class AuthCore:
    def __init__(self, authenticated, event):
        self.event = event
        self.authenticated = authenticated
        self.username = None
        self.selected_profile = None
        self.shared_secret = None
        self.ygg = yggdrasil.YggAuth()

    def start_session(self, username, password = ''):
        rep = {}
        if self.authenticated:
            logger.info("AUTHCORE: Attempting login with username: %s", username)
            rep = self.ygg.authenticate(username, password)
            if rep == None or 'error' in rep:
                logger.error('AUTHCORE: Login Unsuccessful, Response: %s', rep)
                self.event.emit('AUTH_ERR')
                return rep
            if 'selectedProfile' in rep:
                self.selected_profile = rep['selectedProfile']
                self.username = rep['selectedProfile']['name']
                logger.info("AUTHCORE: Logged in as: %s", self.username)
                logger.info("AUTHCORE: Selected Profile: %s", self.selected_profile)
            else:
                self.username = username
        else:
            self.username = username
        return rep

    def gen_shared_secret(self):
        self.shared_secret = Random._UserFriendlyRNG.get_random_bytes(16)
        return self.shared_secret

@pl_announce('Auth')
class AuthPlugin(PluginBase):
    requires = ('Event', 'Net')
    defaults = {
        'authenticated': True,
        'sess_quit': True,
    }
    events = {
        'AUTH_ERR': 'handleAUTHERR',
        'SESS_ERR': 'handleSESSERR',
        'LOGIN<Encryption Request': 'handle_encryption_request',
    }
    def __init__(self, ploader, settings):
        super(self.__class__, self).__init__(ploader, settings)
        self.authenticated = self.settings['authenticated']
        self.sess_quit = self.settings['sess_quit']
        self.auth = AuthCore(self.authenticated, self.event)
        self.auth.gen_shared_secret()
        ploader.provides('Auth', self.auth)

    def handleAUTHERR(self, name, data):
        self.event.kill()

    def handleSESSERR(self, name, data):
        if self.sess_quit:
            self.event.kill()

    #Encryption Key Request - Request for client to start encryption
    def handle_encryption_request(self, name, packet):
        pubkey = packet.data['public_key']
        if self.authenticated:
            serverid = JavaHexDigest(hashlib.sha1(
                packet.data['server_id'].encode('ascii')
                + self.auth.shared_secret
                + pubkey
            ))
            logger.info("AUTHPLUGIN: Attempting to authenticate session with sessionserver.mojang.com")
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
            #if rep != 'OK':
            #	print('Session Authentication Failed, Response:', rep)
            #	self.event.emit('SESS_ERR')
            #	return
            if rep != "":
                logger.warning("AUTHPLUGIN: %s", rep)
            logger.info("AUTHPLUGIN: Session authentication successful")

        rsa_cipher = PKCS1_v1_5.new(RSA.importKey(pubkey))
        self.net.push_packet(
            'LOGIN>Encryption Response',
            {
                'shared_secret': rsa_cipher.encrypt(self.auth.shared_secret),
                'verify_token': rsa_cipher.encrypt(packet.data['verify_token']),
            }
        )
        self.net.enable_crypto(self.auth.shared_secret)
