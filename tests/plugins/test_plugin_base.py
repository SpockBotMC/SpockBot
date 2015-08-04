from unittest import TestCase
from spock.plugins.base import PluginBase

class PluginLoaderMock(object):
    events = {}

    def requires(self, *args, **kwargs):
        return True

    def reg_event_handler(self, event, handler):
        self.events[event] = [] if event not in self.events else self.events[event]
        self.events[event].append(handler)

class TestPluginBase(PluginBase):
    requires = ('Net', 'Auth')
    defaults = {'foo': 'bar'}
    events = {'test': 'callback'}

    def callback(self):
        pass

class PluginBaseTest(TestCase):
    def setUp(self):
        self.ploader = PluginLoaderMock()
        self.plug = TestPluginBase(self.ploader, {})

    def tearDown(self):
        delattr(self, 'ploader')
        delattr(self, 'plug')

    def test_requirements_get_loaded(self):
        self.assertTrue(getattr(self.plug, 'net', False))
        self.assertTrue(getattr(self.plug, 'auth', False))

    def test_default_settings_applied(self):
        # Only assert that settings are set. Checking whether settings and
        # defaults merge correctly should be tested in
        # spock.utils.get_settings.
        self.assertEqual(self.plug.settings['foo'], 'bar')

    def test_event_listeners_registration_succeeds(self):
        self.assertIn(self.plug.callback, self.ploader.events['test'])