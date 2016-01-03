from __future__ import unicode_literals

import logging

try:
    import simplejson as json
except ImportError:
    import json
from six.moves.urllib.error import HTTPError
from six.moves.urllib.request import Request, urlopen

logger = logging.getLogger()


class YggdrasilCore(object):
    ygg_version = 1
    ygg_url = 'https://authserver.mojang.com'

    def __init__(self, username='', password='', client_token='',
                 access_token=''):
        self.username = username
        self.password = password
        self.client_token = client_token
        self.access_token = access_token
        self.available_profiles = []
        self.selected_profile = {}

    def login(self):
        if self.access_token and self.validate():
            return True
        if self.access_token and self.client_token and self.refresh():
            return True
        return self.username and self.password and self.authenticate()

    def logout(self):
        return self.access_token and self.client_token and self.invalidate()

    def _ygg_req(self, endpoint, payload):
        try:
            resp = urlopen(Request(
                url=self.ygg_url + endpoint,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'})
            )
        except HTTPError as e:
            resp = e
        data = resp.read().decode('utf-8')
        return json.loads(data) if data else dict()

    def authenticate(self):
        """
        Generate an access token using an username and password. Any existing
        client token is invalidated if not provided.

        Returns:
            dict: Response or error dict
        """
        endpoint = '/authenticate'

        payload = {
            'agent': {
                'name': 'Minecraft',
                'version': self.ygg_version,
            },
            'username': self.username,
            'password': self.password,
            'clientToken': self.client_token,
        }
        rep = self._ygg_req(endpoint, payload)
        if not rep or 'error' in rep:
            return False
        self.access_token = rep['accessToken']
        self.client_token = rep['clientToken']
        self.available_profiles = rep['availableProfiles']
        self.selected_profile = rep['selectedProfile']
        return True

    def refresh(self):
        """
        Generate an access token with a client/access token pair. Used
        access token is invalidated.

        Returns:
            dict: Response or error dict
        """
        endpoint = '/refresh'

        payload = {
            'accessToken': self.access_token,
            'clientToken': self.client_token,
        }
        rep = self._ygg_req(endpoint, payload)
        if not rep or 'error' in rep:
            return False

        self.access_token = rep['accessToken']
        self.client_token = rep['clientToken']
        self.selected_profile = rep['selectedProfile']
        return True

    def signout(self):
        """
        Invalidate access tokens with a username and password.

        Returns:
            dict: Empty or error dict
        """
        endpoint = '/signout'

        payload = {
            'username': self.username,
            'password': self.password,
        }
        rep = self._ygg_req(endpoint, payload)
        if not rep or 'error' in rep:
            return False
        self.client_token = ''
        self.access_token = ''
        self.available_profiles = []
        self.selected_profile = {}
        return True

    def invalidate(self):
        """
        Invalidate access tokens with a client/access token pair

        Returns:
            dict: Empty or error dict
        """
        endpoint = '/invalidate'

        payload = {
            'accessToken': self.access_token,
            'clientToken': self.client_token,
        }
        self._ygg_req(endpoint, payload)
        self.client_token = ''
        self.access_token = ''
        self.available_profiles = []
        self.selected_profile = {}
        return True

    def validate(self):
        """
        Check if an access token is valid

        Returns:
            dict: Empty or error dict
        """
        endpoint = '/validate'

        payload = dict(accessToken=self.access_token)
        rep = self._ygg_req(endpoint, payload)
        return not bool(rep)
