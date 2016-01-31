"""
Provides the core event loop
"""
import logging
import signal
from collections import defaultdict
from copy import deepcopy

from spockbot.plugins.base import pl_announce
from spockbot.plugins.tools.event import EVENT_UNREGISTER

logger = logging.getLogger('spockbot')


@pl_announce('Event')
class EventPlugin(object):
    def __init__(self, ploader, settings):
        ploader.provides('Event', self)
        self.has_run = False
        self.kill_event = False
        self.event_handlers = defaultdict(list)
        signal.signal(signal.SIGINT, self.kill)
        signal.signal(signal.SIGTERM, self.kill)

    def event_loop(self, once=False):
        if once:
            self.run_once()
        else:
            self.run_continuous()

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
        # the handler list of this event can change during handler execution,
        # so we loop over a copy
        try:
            for handler in self.event_handlers[event][:]:
                d = data.clone() if hasattr(data, 'clone') else deepcopy(data)
                if handler(event, d) == EVENT_UNREGISTER:
                    self.event_handlers[event].remove(handler)
        except:
            logger.debug('EVENTCORE: Exception while emitting %s %s',
                         event, data)
            raise

    def kill(self, *args):
        self.kill_event = True
