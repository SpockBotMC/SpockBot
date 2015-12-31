"""
Provides the core event loop
"""
import copy
import logging
import signal
from collections import defaultdict

from spockbot.plugins.base import pl_announce
from spockbot.plugins.tools.event import EVENT_UNREGISTER

logger = logging.getLogger('spockbot')


class EventCore(object):
    def __init__(self):
        self.has_run = False
        self.kill_event = False
        self.event_handlers = defaultdict(list)
        signal.signal(signal.SIGINT, self.kill)
        signal.signal(signal.SIGTERM, self.kill)

    def event_loop(self, continuous=True):
        if continuous:
            self.run_continuous()
        else:
            self.run_once()

    def run_continuous(self):
        if not self.has_run and not self.kill_event:
            self.has_run = True
            self.emit('event_start')
        while not self.kill_event:
            self.emit('event_tick')
        logger.debug('EVENTCORE: Kill called, shutting down')
        self.emit('event_kill')

    def run_once(self):
        if not self.has_run and not self.kill_event:
            self.has_run = True
            self.emit('event_start')
        if not self.kill_event:
            self.emit('event_tick')
        else:
            logger.debug('EVENTCORE: Kill called, shutting down')
            self.emit('event_kill')

    def reg_event_handler(self, event, handler):
        self.event_handlers[event].append(handler)

    def unreg_event_handler(self, event, handler):
        self.event_handlers[event].remove(handler)

    def emit(self, event, data=None):
        to_remove = []
        # reversed, because handlers can register themselves
        # for the same event they handle, and the new handler
        # is appended to the end of the iterated handler list
        # and immediately run, so an infinite loop can be created
        for handler in reversed(self.event_handlers[event]):
            d = data.clone() if hasattr(data, 'clone') else copy.deepcopy(data)
            if handler(event, d) == EVENT_UNREGISTER:
                to_remove.append(handler)
        for handler in to_remove:
            self.event_handlers[event].remove(handler)

    def kill(self, *args):
        self.kill_event = True


@pl_announce('Event')
class EventPlugin(object):
    def __init__(self, ploader, settings):
        ploader.provides('Event', EventCore())
