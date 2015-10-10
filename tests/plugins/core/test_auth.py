from __future__ import unicode_literals

import hashlib

import mock
from mock.mock import MagicMock

from spockbot.plugins.core.auth import AuthPlugin, java_hex_digest


def test_java_hex_digest():
    negative_hash = java_hex_digest(hashlib.sha1(b'a'))
    assert negative_hash == '-79081bc8055a58031ea2e22346151515c8899848'
    positive_hash = java_hex_digest(hashlib.sha1(b'd'))
    assert positive_hash == '3c363836cf4e16666669a25da280a1865c2d2874'


@mock.patch('spockbot.plugins.core.auth.YggdrasilCore')
def test_auth_init(ygg):
    ploader, settings = MagicMock(), MagicMock()
    auth_plugin = AuthPlugin(ploader, settings)
    ploader.provides.assert_called_once_with('Auth', auth_plugin)
    print(auth_plugin.online_mode)
    # assert auth_plugin.online_mode == settings['online_mode']
    # assert auth_plugin.sess_quit == settings['sess_quit']
    assert auth_plugin.ygg == ygg()
    assert auth_plugin._shared_secret is None
    assert auth_plugin._username is None


def get_mocked_auth_plugin():
    auth_plugin = AuthPlugin(MagicMock(), MagicMock())
    auth_plugin.online_mode = False
    auth_plugin.sess_quit = False
    auth_plugin.ygg = ygg_mock = MagicMock()
    auth_plugin.ygg.password = ''
    auth_plugin.ygg.username = ''
    auth_plugin.event = MagicMock()
    return auth_plugin, ygg_mock


def test_offline_username():
    auth, ygg = get_mocked_auth_plugin()
    auth.online_mode = False
    assert auth.username is None
    auth.username = 'Joe'
    # username should return None till start_session()
    assert auth.username is None
    auth.start_session()
    assert auth.username == 'Joe'
    assert ygg.mock_calls == []


def test_online_username():
    auth, ygg = get_mocked_auth_plugin()
    auth.online_mode = True
    assert auth.username is None
    auth.username = 'Joe'
    auth.ygg.selected_profile = {'name': 'Joe'}
    # username should return None till start_session()
    assert auth.username is None
    # Test failing login
    ygg.login.return_value = False
    auth.start_session()
    assert auth.username is None
    # Test succeeding login
    ygg.login.return_value = True
    auth.start_session()
    assert auth.username == 'Joe'


def test_password():
    auth, ygg = get_mocked_auth_plugin()
    assert auth.password is False
    # Empty password is no password
    auth.password = ''
    assert auth.password is False
    # Normal password
    auth.password = 'password'
    assert auth.password is True


def test_start_session_online_success():
    auth, ygg = get_mocked_auth_plugin()
    auth.online_mode = True
    ygg.login.return_value = True
    res = auth.start_session()
    assert res
    assert not auth.event.called
    assert auth.username


def test_start_session_online_failure():
    auth, ygg = get_mocked_auth_plugin()
    auth.online_mode = True
    ygg.login.return_value = False
    res = auth.start_session()
    assert not res
    assert auth.event.emit.called
    assert not auth.username


@mock.patch('spockbot.plugins.core.auth.os.urandom')
def test_get_shared_secret(rnd):
    auth, ygg = get_mocked_auth_plugin()
    assert not rnd.called
    assert not auth._shared_secret
    ss = auth.shared_secret
    assert auth.shared_secret == ss
    assert rnd.called


def test_handle_auth_error():
    auth, _ = get_mocked_auth_plugin()
    auth.handle_auth_error(None, None)
    assert auth.event.kill.called


def test_handle_session_error():
    auth, _ = get_mocked_auth_plugin()
    auth.handle_session_error(None, None)
    assert not auth.event.kill.called
    auth.sess_quit = True
    auth.handle_session_error(None, None)
    assert auth.event.kill.called
