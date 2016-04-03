"""
Provides an asynchronous multi-socket selector with a poll method
built on top of select.select for cross-platform compatibility.

After polling select, two events are emitted for each socket and kind-of-ready,
``select_<kind>`` and ``select_<kind>_<sock.fileno()>``, where
``<kind>`` is one of ``recv, send, err``.

The event payload is always the fileno of the corresponding socket.
(The event plugin deep-copies the payload, but sockets are not serializable)

Note that the event loop is stopped during selecting. This is good in that
the loop does not consume 100% CPU, but it means you have to register
at least a slow timer if you do stuff on ``event_tick`` and
expect it to be emitted frequently.
"""

import logging
import select

from spockbot.plugins.base import PluginBase, pl_announce

logger = logging.getLogger('spockbot')


@pl_announce('Select')
class SelectPlugin(PluginBase):
    requires = ('Event', 'Timers')

    def __init__(self, ploader, settings):
        super(SelectPlugin, self).__init__(ploader, settings)
        self.sockets = set()
        self.sending = set()
        ploader.provides('Select', self)

    def register_socket(self, sock):
        """``poll()``ing will emit events when this socket is ready."""
        self.sockets.add(sock)

    def unregister_socket(self, sock):
        self.sockets.remove(sock)

    def schedule_sending(self, sock):
        """Emit one event the next time this socket is ready to send."""
        self.sending.add(sock)

    def poll(self):
        timeout = self.timers.get_timeout()
        if timeout < 0:
            timeout = 5  # do not hang

        select_args = [
            tuple(self.sockets),
            tuple(self.sending),
            tuple(self.sockets),
            timeout,
        ]
        self.sending.clear()

        try:
            ready_lists = select.select(*select_args)
        except select.error as e:
            logger.error('SELECTSOCKET: Socket Error: "%s" %s', str(e), e.args)
            return

        for ready_socks, kind in zip(ready_lists, ('recv', 'send', 'err')):
            for sock in ready_socks:
                self.event.emit('select_%s' % kind, sock.fileno())
                self.event.emit('select_%s_%s' % (kind, sock.fileno()),
                                sock.fileno())
