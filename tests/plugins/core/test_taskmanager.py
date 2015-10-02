from collections import defaultdict
from unittest import TestCase

from spockbot.plugins.core.taskmanager import TaskManager
from spockbot.plugins.tools.task import Task


class EventMock(object):
    def __init__(self):
        self.handlers = defaultdict(list)

    def reg_event_handler(self, evt, handler):
        self.handlers[evt].append(handler)

    def emit(self, event, data):
        to_remove = []
        for handler in reversed(self.handlers[event]):
            if handler(event, data):
                to_remove.append(handler)
            else:
                raise AssertionError('%s %s' % (handler.__name__, handler))

        for handler in to_remove:
            self.handlers[event].remove(handler)


class PluginLoaderMock(object):
    def provides(self, ident, obj):
        self.provides_ident = ident
        self.provides_obj = obj

    def requires(self, plug_name):
        assert plug_name == 'Event', 'Unexpected requirement %s' % plug_name
        return EventMock()


class TaskManagerTest(TestCase):

    def setUp(self):
        ploader = PluginLoaderMock()
        self.task_manager = TaskManager(ploader, {})
        assert ploader.provides_ident == 'TaskManager'
        assert isinstance(ploader.provides_obj, TaskManager)

    def test_run_task(self):
        def some_task(level):
            if level <= 0:
                raise StopIteration('We are done!', level)

            # one event name
            event, data = yield 'some_event'
            self.assertEqual('some_event', event)
            self.assertDictEqual({'some': 'data'}, data)

            # multiple event names
            event, data = yield 'other_event', 'never_emitted', 'this_neither'
            self.assertEqual('other_event', event)
            self.assertDictEqual({'other': 'data'}, data)

            # event name + check
            event, data = yield 'cool_event', lambda e, d: True
            self.assertEqual('cool_event', event)
            self.assertDictEqual({'more': 'data'}, data)

            # subtask
            event, data = yield some_task(level - 1)
            self.assertEqual(None, event)
            self.assertTupleEqual(('We are done!', level - 1), data)

            raise StopIteration('We are done!', level)

        def emit_them(level):
            """Recursively emit and check the events waited for by the task"""
            if level <= 0:
                return

            self.assertIn('some_event', self.task_manager.event.handlers,
                          'Event not registered')

            self.task_manager.event.emit('some_event', {'some': 'data'})
            self.assertFalse(self.task_manager.event.handlers['some_event'],
                             'Emitted event not unregistered')

            self.assertIn('other_event', self.task_manager.event.handlers,
                          'Event not registered')
            self.assertIn('never_emitted', self.task_manager.event.handlers,
                          'Event not registered')
            self.assertIn('this_neither', self.task_manager.event.handlers,
                          'Event not registered')

            self.task_manager.event.emit('other_event', {'other': 'data'})
            self.assertFalse(self.task_manager.event.handlers['other_Event'],
                             'Emitted event not unregistered')

            self.assertIn('cool_event', self.task_manager.event.handlers,
                          'Event not registered')

            self.task_manager.event.emit('cool_event', {'more': 'data'})
            self.assertFalse(self.task_manager.event.handlers['cool_event'],
                             'Emitted event not unregistered')

            emit_them(level - 1)

        done = [False]  # because we can't use nonlocal in Python 2.7

        test_case = self  # to make flake8 happy

        class SomeParent(object):
            def on_success(self, data):
                done[0] = True

            def on_error(self, e):
                test_case.fail('Task failed with %s: %s'
                               % (e.__class__.__name__, e.args))

        levels = 3

        task = some_task(levels)
        parent = SomeParent()

        ret = self.task_manager.run_task(task, parent)
        self.assertIsInstance(ret, Task)

        emit_them(levels)

        assert done[0]
