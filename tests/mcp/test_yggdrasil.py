from __future__ import unicode_literals

import mock
from mock.mock import MagicMock

from six.moves.urllib.error import HTTPError

from spockbot.mcp.yggdrasil import YggdrasilCore

ygg_auth_error = {'error': 'ForbiddenOperationException',
                  'errorMessage': 'Invalid credentials. Invalid username or '
                                  'password.'}

ygg_auth_user_pass = {'accessToken': '01234567890123456789012345678901',
                      'availableProfiles': [
                          {'id': '01234567890123456789012345678901',
                           'name': 'username'}],
                      'clientToken': '01234567890123456789012345678901',
                      'selectedProfile': {
                          'id': '01234567890123456789012345678901',
                          'name': 'username'}}


@mock.patch('spockbot.mcp.yggdrasil.Request')
@mock.patch('spockbot.mcp.yggdrasil.urlopen')
def test_request_is_done(urlopen, request):
    decode = urlopen.return_value.read.return_value.decode
    decode.return_value = '{"test": 1}'
    ygg = YggdrasilCore()
    assert not urlopen.called
    assert not request.called
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
    assert urlopen.return_value.read.called
    assert decode.called

    assert res == {'test': 1}


@mock.patch('spockbot.mcp.yggdrasil.Request')
@mock.patch('spockbot.mcp.yggdrasil.urlopen')
def test_request_raises_error(urlopen, request):
    exception_data = MagicMock()
    exception_data.read.return_value.decode.return_value = '{"error": 1}'
    urlopen.side_effect = HTTPError('', '', '', '', exception_data)

    ygg = YggdrasilCore()
    assert not urlopen.called
    assert not request.called
    res = ygg._ygg_req('/test', {'a': 'b'})

    # Read the response
    assert exception_data.read.called
    assert exception_data.read.return_value.decode.called

    assert res == {'error': 1}


def test_yggdrasil_initialization():
    ygg = YggdrasilCore()
    assert '' == ygg.username
    assert '' == ygg.password
    assert '' == ygg.client_token
    assert '' == ygg.access_token


def test_authenticate_success():
    ygg = YggdrasilCore()
    ygg._ygg_req = ygg_req = mock.MagicMock()
    ygg_req.return_value = {'accessToken': 'myaccess',
                            'clientToken': 'mytoken',
                            'availableProfiles': ['a', 'b'],
                            'selectedProfile': 'a'}

    ygg.username = 'user'
    ygg.password = 'pass'
    ygg.client_token = 'clienttoken'

    res = ygg.authenticate()

    ygg_req.assert_called_once_with('/authenticate', {
        'agent': {
            'name': 'Minecraft',
            'version': 1,
        },
        'username': 'user',
        'password': 'pass',
        'clientToken': 'clienttoken',
    })

    assert ygg.username == 'user'
    assert ygg.password == 'pass'
    assert ygg.client_token == 'mytoken'
    assert ygg.access_token == 'myaccess'
    assert res


def test_authenticate_failure():
    ygg = YggdrasilCore()
    ygg._ygg_req = ygg_req = mock.MagicMock()
    ygg_req.return_value = {'error': 1}

    ygg.username = 'user'
    ygg.password = 'pass'
    ygg.client_token = 'clienttoken'
    res = ygg.authenticate()

    ygg_req.assert_called_once_with('/authenticate', {
        'agent': {
            'name': 'Minecraft',
            'version': 1,
        },
        'username': 'user',
        'password': 'pass',
        'clientToken': 'clienttoken',
    })

    assert ygg.username == 'user'
    assert ygg.password == 'pass'
    assert ygg.client_token == 'clienttoken'
    assert '' == ygg.access_token
    assert not res


def test_refresh_success():
    ygg = YggdrasilCore()
    ygg._ygg_req = ygg_req = mock.MagicMock()
    ygg_req.return_value = {'accessToken': 'myaccess',
                            'clientToken': 'mytoken',
                            'availableProfiles': ['a', 'b'],
                            'selectedProfile': 'a'}

    ygg.client_token = 'clienttoken'
    ygg.access_token = 'accesstoken'
    res = ygg.refresh()

    ygg_req.assert_called_once_with('/refresh', {
        'accessToken': 'accesstoken',
        'clientToken': 'clienttoken',
    })

    assert ygg.client_token == 'mytoken'
    assert ygg.access_token == 'myaccess'
    assert '' == ygg.username
    assert '' == ygg.password
    assert res


def test_refresh_failure():
    ygg = YggdrasilCore()
    ygg._ygg_req = ygg_req = mock.MagicMock()
    ygg_req.return_value = {'error': 1}

    ygg.client_token = 'clienttoken'
    ygg.access_token = 'accesstoken'
    res = ygg.refresh()

    ygg_req.assert_called_once_with('/refresh', {
        'accessToken': 'accesstoken',
        'clientToken': 'clienttoken',
    })

    assert '' == ygg.username
    assert '' == ygg.password
    assert ygg.client_token == 'clienttoken'
    assert ygg.access_token == 'accesstoken'
    assert not res


def test_signout():
    ygg = YggdrasilCore()
    ygg._ygg_req = ygg_req = mock.MagicMock()
    ygg_req.return_value = {'whatever': 'dict'}

    ygg.username = 'user'
    ygg.password = 'pass'
    res = ygg.signout()

    ygg_req.assert_called_once_with('/signout', {
        'username': 'user',
        'password': 'pass',
    })

    assert ygg.username == 'user'
    assert ygg.password == 'pass'
    assert '' == ygg.client_token
    assert '' == ygg.access_token
    assert res


def test_invalidate():
    ygg = YggdrasilCore()
    ygg._ygg_req = ygg_req = mock.MagicMock()
    ygg_req.return_value = {'whatever': 'dict'}

    ygg.client_token = 'clienttoken'
    ygg.access_token = 'accesstoken'
    res = ygg.invalidate()

    ygg_req.assert_called_once_with('/invalidate', {
        'clientToken': 'clienttoken',
        'accessToken': 'accesstoken',
    })

    assert '' == ygg.username
    assert '' == ygg.password
    assert '' == ygg.client_token
    assert '' == ygg.access_token
    assert res


def test_validate_success():
    ygg = YggdrasilCore()
    ygg._ygg_req = ygg_req = mock.MagicMock()
    ygg_req.return_value = {}

    ygg.access_token = 'accesstoken'
    res = ygg.validate()

    ygg_req.assert_called_once_with('/validate', {
        'accessToken': 'accesstoken',
    })

    assert '' == ygg.username
    assert '' == ygg.password
    assert '' == ygg.client_token
    assert 'accesstoken' == ygg.access_token
    assert res


def test_validate_error():
    ygg = YggdrasilCore()
    ygg._ygg_req = ygg_req = mock.MagicMock()
    ygg_req.return_value = {'whatever': 'dict'}

    ygg.access_token = 'accesstoken'
    res = ygg.validate()

    ygg_req.assert_called_once_with('/validate', {
        'accessToken': 'accesstoken',
    })

    assert '' == ygg.username
    assert '' == ygg.password
    assert '' == ygg.client_token
    assert 'accesstoken' == ygg.access_token
    assert not res
