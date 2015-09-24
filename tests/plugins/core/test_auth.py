from __future__ import unicode_literals

import hashlib
import mock
from mock.mock import MagicMock

from spock.plugins.core.auth import AuthPlugin, java_hex_digest


def test_java_hex_digest():
    negative_hash = java_hex_digest(hashlib.sha1(b'a'))
    assert negative_hash == '-79081bc8055a58031ea2e22346151515c8899848'
    positive_hash = java_hex_digest(hashlib.sha1(b'd'))
    assert positive_hash == '3c363836cf4e16666669a25da280a1865c2d2874'


@mock.patch('spock.plugins.core.auth.YggdrasilCore')
def test_auth_init():
    ploader, settings = MagicMock(), MagicMock()
    auth_plugin = AuthPlugin(ploader, settings)
    ploader.provides.assert_called_once_with('Auth', auth_plugin)
    assert auth_plugin.online_mode == settings['online_mode']
    assert auth_plugin.sess_quit == settings['sess_quit']
    assert auth_plugin.ygg
    assert auth_plugin._shared_secret == None
    assert auth_plugin._username == None


@mock.patch('spock.plugins.core.auth.YggdrasilCore')
def get_mocked_auth_plugin():
    auth_plugin = AuthPlugin(MagicMock(), MagicMock())
    auth_plugin.online_mode = False
    auth_plugin.sess_quit = True
    auth_plugin.ygg = ygg_mock = MagicMock()
    return auth_plugin, ygg_mock


def test_offline_username():
    auth, ygg = get_mocked_auth_plugin()
    auth.online_mode = False
    assert auth.username == None
    auth.username = 'Joe'
    # username should return None till start_session()
    assert auth.username == None
    auth.start_session()
    assert auth.username == 'Joe'
    assert ygg.calls == []


def test_online_username():
    auth, ygg = get_mocked_auth_plugin()
    auth.online_mode = True
    assert auth.username == None
    auth.username = 'Joe'
    # username should return None till start_session()
    assert auth.username == None
    # Test failing login
    ygg.login.return_value = False
    auth.start_session()
    assert auth.username == None
    # Test succeeding login
    ygg.login.return_value = True
    auth.start_session()
    assert auth.username == 'Joe'


def test_password():
    auth, ygg = get_mocked_auth_plugin()
    assert auth.password == False
    # Empty password is no password
    auth.password = ''
    assert auth.password == False
    # Normal password
    auth.password = 'password'
    assert auth.password == True
