"""
Provides the core event loop
"""
import signal
import copy
from collections import defaultdict
from spock.utils import pl_announce

import logging
logger = logging.getLogger('spock')

class EventCore:
    def __init__(self):
        self.kill_event = False
        self.event_handlers = defaultdict(list)
        signal.signal(signal.SIGINT, self.kill)
        signal.signal(signal.SIGTERM, self.kill)

    def event_loop(self):
        while not self.kill_event:
            self.emit('event_tick')
        logger.info('EVENTCORE: Kill called, shutting down')
        self.emit('kill')

    def reg_event_handler(self, event, handler):
        self.event_handlers[event].append(handler)

    def emit(self, event, data = None):
        to_remove = []
        # reversed, because handlers can register themselves
        # for the same event they handle, and the new handler
        # is appended to the end of the iterated handler list
        # and immediately run, so an infinite loop can be created
        for handler in reversed(self.event_handlers[event]):
            if handler(
                event,
                data.clone() if hasattr(data, 'clone') else copy.deepcopy(data)
            ):
                to_remove.append(handler)
        for handler in to_remove:
            self.event_handlers[event].remove(handler)

    def kill(self, *args):
        self.kill_event = True

@pl_announce('Event')
class EventPlugin:
    def __init__(self, ploader, settings):
        ploader.provides('Event', EventCore())
