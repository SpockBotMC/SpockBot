from __future__ import unicode_literals

import hashlib

import mock
from mock.mock import MagicMock

from spockbot.plugins.core.auth import AuthCore, AuthPlugin, java_hex_digest


def test_java_hex_digest():
    negative_hash = java_hex_digest(hashlib.sha1(b'a'))
    assert negative_hash == '-79081bc8055a58031ea2e22346151515c8899848'
    positive_hash = java_hex_digest(hashlib.sha1(b'd'))
    assert positive_hash == '3c363836cf4e16666669a25da280a1865c2d2874'


def get_mocked_auth_core():
    event_mock = MagicMock()
    auth_core = AuthCore(event_mock, MagicMock(), MagicMock())
    auth_core.online_mode = False
    auth_core.auth_timeout = 3
    auth_core.ygg = ygg_mock = MagicMock()
    auth_core.ygg.password = ''
    auth_core.ygg.username = ''
    return auth_core, event_mock, ygg_mock


def test_offline_username():
    auth, event, ygg = get_mocked_auth_core()
    auth.online_mode = False
    assert auth.username is None
    auth.username = 'Joe'
    # username should return None till start_session()
    assert auth.username is None
    auth.start_session()
    assert auth.username == 'Joe'
    assert ygg.mock_calls == []


def test_online_username():
    auth, event, ygg = get_mocked_auth_core()
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
    auth, event, ygg = get_mocked_auth_core()
    assert auth.password is False
    # Empty password is no password
    auth.password = ''
    assert auth.password is False
    # Normal password
    auth.password = 'password'
    assert auth.password is True


def test_start_session_online_success():
    auth, event, ygg = get_mocked_auth_core()
    auth.online_mode = True
    ygg.login.return_value = True
    res = auth.start_session()
    assert res
    assert not event.called
    assert auth.username


def test_start_session_online_failure():
    auth, event, ygg = get_mocked_auth_core()
    auth.online_mode = True
    ygg.login.return_value = False
    res = auth.start_session()
    assert not res
    assert event.emit.called
    assert not auth.username


@mock.patch('spockbot.plugins.core.auth.os.urandom')
def test_get_shared_secret(rnd):
    auth, event, ygg = get_mocked_auth_core()
    assert not rnd.called
    assert not auth._shared_secret
    ss = auth.shared_secret
    assert auth.shared_secret == ss
    assert rnd.called


def get_mocked_auth_plugin():
    auth_plugin = AuthPlugin(MagicMock(), MagicMock())
    auth_plugin.auth_quit = False
    auth_plugin.sess_quit = False
    auth_plugin.event = MagicMock()
    return auth_plugin


def test_handle_auth_error():
    auth = get_mocked_auth_plugin()
    auth.handle_auth_error(None, None)
    assert not auth.event.kill.called
    auth.auth_quit = True
    auth.handle_auth_error(None, None)
    assert auth.event.kill.called


def test_handle_session_error():
    auth = get_mocked_auth_plugin()
    auth.handle_session_error(None, None)
    assert not auth.event.kill.called
    auth.sess_quit = True
    auth.handle_session_error(None, None)
    assert auth.event.kill.called
