import json
#This is for python2 compatibility 
try:
    import urllib.request as request
    from urllib.error import HTTPError
except ImportError:
    import urllib2 as request
    from urllib2 import HTTPError

class YggAuth:
    def __init__(self, 
        client_token=None, 
        access_token=None, 
        username=None, 
        password=None
    ):
        self.username = username
        self.password = password
        self.client_token = client_token

        self.access_token = None #validate needs self.access_token to exist
        self.access_token = (
            None if self.validate(access_token) else access_token
        )

    def _gen_req(self, endpoint, payload):
        url = 'https://authserver.mojang.com' + endpoint
        data = json.dumps(payload).encode('utf-8')
        headers = {'Content-Type': 'application/json'}
        return request.Request(url, data, headers)

    def _gen_rep(self, req):
        try:
            rep = request.urlopen(req)
        except HTTPError as reperr:
            rep = reperr
        data = rep.read().decode('utf-8')
        return json.loads(data) if data else None

    def _ygg_req(self, endpoint, payload):
        return self._gen_rep(self._gen_req(endpoint, payload))

    #Generate an access token using a username and password
    #(Any existing client token is invalidated if not provided)
    #Returns response dict on success, otherwise error dict
    def authenticate(self, username=None, password=None, client_token=None):
        endpoint = '/authenticate'
        payload = {
            'agent': {
                'name': 'Minecraft',
                'version': 1,
            },
        }
        if username:
            self.username = username
        payload['username'] = self.username
        if password:
            self.password = password
        payload['password'] = self.password
        payload['clientToken'] = client_token if client_token else self.client_token
        rep = self._ygg_req(endpoint, payload)
        if rep != None and 'error' not in rep:
            self.access_token = rep['accessToken']
            self.client_token = rep['clientToken']
        return rep

    #Generate an access token with a client/access token pair
    #(The used access token is invalidated)
    #Returns response dict on success, otherwise error dict
    def refresh(self, client_token=None, access_token=None):
        endpoint = '/refresh'
        payload = {}
        payload['accessToken'] = access_token if access_token else self.access_token
        payload['clientToken'] = client_token if client_token else self.client_token
        rep = self._ygg_req(endpoint, payload)
        if 'error' not in rep:
            self.access_token = rep['accessToken']
            self.client_token = rep['clientToken']
        return rep

    #Invalidate access tokens with a username and password
    #Returns None on success, otherwise error dict
    def signout(self, username=None, password=None):
        endpoint = '/signout'
        payload = {}
        payload['username'] = username if username else self.username
        payload['password'] = password if password else self.password
        return self._ygg_req(endpoint, payload)

    #Invalidate access tokens with a client/access token pair
    #Returns None on success, otherwise error dict
    def invalidate(self, client_token=None, access_token=None):
        endpoint = '/invalidate'
        payload = {}
        payload['accessToken'] = access_token if access_token else self.access_token
        payload['clientToken'] = client_token if client_token else self.client_token
        return self._ygg_req(endpoint, payload)

    #Check if an access token is valid
    #Returns None on success (ie valid access token), otherwise error dict
    def validate(self, access_token=None):
        endpoint = '/validate'
        payload = {}
        payload['accessToken'] = access_token if access_token else self.access_token
        return self._ygg_req(endpoint, payload)
