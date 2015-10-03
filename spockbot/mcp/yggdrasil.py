from __future__ import unicode_literals
# This is for python2 compatibility
try:
    import simplejson as json
except ImportError:
    import json
from six.moves.urllib.error import HTTPError
from six.moves.urllib.request import Request, urlopen


class YggAuth(object):
    def __init__(self):
        self.username = None
        self.password = None
        self.client_token = None
        self.access_token = None

    def _ygg_req(self, endpoint, payload):
        try:
            resp = urlopen(Request(
                url='https://authserver.mojang.com' + endpoint,
                data=json.dumps(payload).encode('utf-8'),
                headers={'Content-Type': 'application/json'})
            )
        except HTTPError as e:
            resp = e
        data = resp.read().decode('utf-8')
        return json.loads(data) if data else dict()

    def authenticate(self, username=None, password=None, client_token=None):
        """
        Generate an access token using an username and password. Any existing
        client token is invalidated if not provided.

        Returns:
            dict: Response or error dict
        """
        endpoint = '/authenticate'
        self.username = username or self.username
        self.password = password or self.password
        self.client_token = client_token or self.client_token

        payload = {
            'agent': {
                'name': 'Minecraft',
                'version': 1,
            },
            'username': self.username,
            'password': self.password,
            'clientToken': self.client_token,
        }
        rep = self._ygg_req(endpoint, payload)
        if rep and 'error' not in rep:
            self.access_token = rep['accessToken']
            self.client_token = rep['clientToken']
        return rep

    def refresh(self, client_token=None, access_token=None):
        """
        Generate an access token with a client/access token pair. Used
        access token is invalidated.

        Returns:
            dict: Response or error dict
        """
        endpoint = '/refresh'
        self.access_token = access_token or self.access_token
        self.client_token = client_token or self.client_token

        payload = {
            'accessToken': self.access_token,
            'clientToken': self.client_token,
        }
        rep = self._ygg_req(endpoint, payload)
        if rep and 'error' not in rep:
            self.access_token = rep['accessToken']
            self.client_token = rep['clientToken']
        return rep

    def signout(self, username=None, password=None):
        """
        Invalidate access tokens with a username and password.

        Returns:
            dict: Empty or error dict
        """
        endpoint = '/signout'
        self.username = username or self.username
        self.password = password or self.username

        payload = {
            'username': self.username,
            'password': self.password,
        }
        return self._ygg_req(endpoint, payload)

    def invalidate(self, client_token=None, access_token=None):
        """
        Invalidate access tokens with a client/access token pair

        Returns:
            dict: Empty or error dict
        """
        endpoint = '/invalidate'
        self.access_token = access_token or self.access_token
        self.client_token = client_token or self.client_token

        payload = {
            'accessToken': self.access_token,
            'clientToken': self.client_token,
        }
        return self._ygg_req(endpoint, payload)

    def validate(self, access_token=None):
        """
        Check if an access token is valid

        Returns:
            dict: Empty or error dict
        """
        endpoint = '/validate'
        self.access_token = access_token or self.access_token

        payload = dict(accessToken=self.access_token)
        return self._ygg_req(endpoint, payload)
