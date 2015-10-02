from __future__ import unicode_literals

import unittest

import mock
from mock.mock import MagicMock

from six.moves.urllib.error import HTTPError

from spockbot.mcp.yggdrasil import YggAuth


@mock.patch('spockbot.mcp.yggdrasil.Request')
@mock.patch('spockbot.mcp.yggdrasil.urlopen')
class YggAuthRequestTest(unittest.TestCase):
    def test_request_is_done(self, urlopen, request):
        decode = urlopen.return_value.read.return_value.decode
        decode.return_value = '{"test": 1}'
        ygg = YggAuth()
        self.assertFalse(urlopen.called)
        self.assertFalse(request.called)
        res = ygg._ygg_req('/test', [{'a': 'b'}, 'c', 'd', 'e'])

        # First create the request
        request.assert_called_once_with(
            url='https://authserver.mojang.com/test',
            data=b'[{"a": "b"}, "c", "d", "e"]',
            headers={'Content-Type': 'application/json'}
        )

        # Then send it
        urlopen.assert_called_once_with(request.return_value)

        # Read the response
        self.assertTrue(urlopen.return_value.read.called)
        self.assertTrue(decode.called)

        self.assertEqual(res, {'test': 1})

    def test_request_raises_error(self, urlopen, request):
        exception_data = MagicMock()
        exception_data.read.return_value.decode.return_value = '{"error": 1}'
        urlopen.side_effect = HTTPError('', '', '', '', exception_data)

        ygg = YggAuth()
        self.assertFalse(urlopen.called)
        self.assertFalse(request.called)
        res = ygg._ygg_req('/test', {'a': 'b'})

        # Read the response
        self.assertTrue(exception_data.read.called)
        self.assertTrue(exception_data.read.return_value.decode.called)

        self.assertEqual(res, {'error': 1})


@mock.patch('spockbot.mcp.yggdrasil.YggAuth._ygg_req')
class YggAuthTest(unittest.TestCase):
    def setUp(self):
        self.ygg = YggAuth()
        self.assertFalse(self.ygg.username)
        self.assertFalse(self.ygg.password)
        self.assertFalse(self.ygg.client_token)
        self.assertFalse(self.ygg.access_token)

    def test_authenticate_success(self, ygg_req):
        ygg_req.return_value = {'accessToken': 'myaccess',
                                'clientToken': 'mytoken'}

        res = self.ygg.authenticate('user', 'pass', 'clienttoken')

        ygg_req.assert_called_once_with('/authenticate', {
            'agent': {
                'name': 'Minecraft',
                'version': 1,
            },
            'username': 'user',
            'password': 'pass',
            'clientToken': 'clienttoken',
        })

        self.assertEqual(self.ygg.username, 'user')
        self.assertEqual(self.ygg.password, 'pass')
        self.assertEqual(self.ygg.client_token, 'mytoken')
        self.assertEqual(self.ygg.access_token, 'myaccess')

        self.assertEqual(res, ygg_req.return_value)

    def test_authenticate_failure(self, ygg_req):
        ygg_req.return_value = {'error': 1}

        res = self.ygg.authenticate('user', 'pass', 'clienttoken')

        ygg_req.assert_called_once_with('/authenticate', {
            'agent': {
                'name': 'Minecraft',
                'version': 1,
            },
            'username': 'user',
            'password': 'pass',
            'clientToken': 'clienttoken',
        })

        self.assertEqual(self.ygg.username, 'user')
        self.assertEqual(self.ygg.password, 'pass')
        self.assertEqual(self.ygg.client_token, 'clienttoken')
        self.assertEqual(self.ygg.access_token, None)

        self.assertEqual(res, ygg_req.return_value)

    def test_refresh_success(self, ygg_req):
        ygg_req.return_value = {'accessToken': 'myaccess',
                                'clientToken': 'mytoken'}

        res = self.ygg.refresh('clienttoken', 'accesstoken')

        ygg_req.assert_called_once_with('/refresh', {
            'accessToken': 'accesstoken',
            'clientToken': 'clienttoken',
        })

        self.assertEqual(self.ygg.username, None)
        self.assertEqual(self.ygg.password, None)
        self.assertEqual(self.ygg.client_token, 'mytoken')
        self.assertEqual(self.ygg.access_token, 'myaccess')

        self.assertEqual(res, ygg_req.return_value)

    def test_refresh_failure(self, ygg_req):
        ygg_req.return_value = {'error': 1}

        res = self.ygg.refresh('clienttoken', 'accesstoken')

        ygg_req.assert_called_once_with('/refresh', {
            'accessToken': 'accesstoken',
            'clientToken': 'clienttoken',
        })

        self.assertEqual(self.ygg.username, None)
        self.assertEqual(self.ygg.password, None)
        self.assertEqual(self.ygg.client_token, 'clienttoken')
        self.assertEqual(self.ygg.access_token, 'accesstoken')

        self.assertEqual(res, ygg_req.return_value)

    def test_signout(self, ygg_req):
        ygg_req.return_value = {'whatever': 'dict'}

        res = self.ygg.signout('user', 'pass')

        ygg_req.assert_called_once_with('/signout', {
            'username': 'user',
            'password': 'pass',
        })

        self.assertEqual(self.ygg.username, 'user')
        self.assertEqual(self.ygg.password, 'pass')
        self.assertEqual(self.ygg.client_token, None)
        self.assertEqual(self.ygg.access_token, None)

        self.assertEqual(res, ygg_req.return_value)

    def test_invalidate(self, ygg_req):
        ygg_req.return_value = {'whatever': 'dict'}

        res = self.ygg.invalidate('clienttoken', 'accesstoken')

        ygg_req.assert_called_once_with('/invalidate', {
            'clientToken': 'clienttoken',
            'accessToken': 'accesstoken',
        })

        self.assertEqual(self.ygg.username, None)
        self.assertEqual(self.ygg.password, None)
        self.assertEqual(self.ygg.client_token, 'clienttoken')
        self.assertEqual(self.ygg.access_token, 'accesstoken')

        self.assertEqual(res, ygg_req.return_value)

    def test_validate(self, ygg_req):
        ygg_req.return_value = {'whatever': 'dict'}

        res = self.ygg.validate('accesstoken')

        ygg_req.assert_called_once_with('/validate', {
            'accessToken': 'accesstoken',
        })

        self.assertEqual(self.ygg.username, None)
        self.assertEqual(self.ygg.password, None)
        self.assertEqual(self.ygg.client_token, None)
        self.assertEqual(self.ygg.access_token, 'accesstoken')

        self.assertEqual(res, ygg_req.return_value)
