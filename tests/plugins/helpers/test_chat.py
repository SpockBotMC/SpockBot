from unittest import TestCase

from spockbot.plugins.helpers.chat import ChatCore, ChatPlugin


class DataDict(dict):
    def __init__(self, **kwargs):
        super(DataDict, self).__init__(**kwargs)
        self.__dict__.update(kwargs)


class PluginLoaderMock(object):
    events = {}

    def provides(self, ident, obj):
        self.provides_ident = ident
        self.provides_obj = obj

    def requires(self, requirement):
        if requirement == 'Net':
            return NetMock()
        if requirement == 'Event':
            return EventMock()
        else:
            raise AssertionError('Unexpected requirement %s' % requirement)

    def reg_event_handler(self, event, handler):
        self.events[event] = [] if event not in self.events else self.events[
            event]
        self.events[event].append(handler)


class NetMock(object):
    idents = []
    datas = []

    def push_packet(self, ident, data):
        data_dict = DataDict(**data)
        self.idents.append(ident)
        self.datas.append(data_dict)


class EventMock(object):
    def emit(self, name, data):
        return True


class ChatPluginTest(TestCase):
    def setUp(self):
        ploader = PluginLoaderMock()
        self.plug = ChatPlugin(ploader, {})
        assert ploader.provides_ident == 'Chat'
        assert isinstance(ploader.provides_obj, ChatCore)

    def test_chat(self):
        self.plug.chatcore.chat('Hello')
        self.assertEqual(NetMock.datas[-1].message, 'Hello')

    def test_whisper(self):
        self.plug.chatcore.whisper('Guy', 'Hello')
        self.assertEqual(NetMock.datas[-1].message, '/tell Guy Hello')
