"""
Provides an asynchronous, crypto and compression aware socket for connecting to
servers and processing incoming packet data.
Coordinates with the Timers plugin to honor wall-clock timers
"""

import logging
import select
import socket
import time

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import ciphers
from cryptography.hazmat.primitives.ciphers import algorithms, modes

from spockbot.mcp import mcpacket, proto
from spockbot.mcp.bbuff import BoundBuffer, BufferUnderflowException
from spockbot.plugins.base import PluginBase, pl_announce

logger = logging.getLogger('spockbot')
backend = default_backend()


class AESCipher(object):
    def __init__(self, shared_secret):
        cipher = ciphers.Cipher(algorithms.AES(shared_secret),
                                modes.CFB8(shared_secret), backend)
        # Name courtesy of dx
        self.encryptifier = cipher.encryptor()
        self.decryptifier = cipher.decryptor()

    def encrypt(self, data):
        return self.encryptifier.update(data)

    def decrypt(self, data):
        return self.decryptifier.update(data)


class SelectSocket(socket.socket):
    """
    Provides an asynchronous socket with a poll method built on
    top of select.select for cross-platform compatiability
    """
    def __init__(self, timer):
        super(SelectSocket, self).__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.sending = False
        self.timer = timer

    def poll(self):
        flags = []
        if self.sending:
            self.sending = False
            slist = [(self,), (self,), (self,)]
        else:
            slist = [(self,), (), (self,)]
        timeout = self.timer.get_timeout()
        if timeout >= 0:
            slist.append(timeout)
        try:
            rlist, wlist, xlist = select.select(*slist)
        except select.error as e:
            logger.error("SELECTSOCKET: Socket Error: %s", str(e))
            rlist, wlist, xlist = [], [], []
        if rlist:
            flags.append('SOCKET_RECV')
        if wlist:
            flags.append('SOCKET_SEND')
        if xlist:
            flags.append('SOCKET_ERR')
        return flags


class NetCore(object):
    def __init__(self, sock, event):
        self.sock = sock
        self.event = event
        self.host = None
        self.port = None
        self.connected = False
        self.encrypted = False
        self.proto_state = proto.HANDSHAKE_STATE
        self.comp_state = proto.PROTO_COMP_OFF
        self.comp_threshold = -1
        self.sbuff = b''
        self.rbuff = BoundBuffer()

    def connect(self, host='localhost', port=25565):
        self.host = host
        self.port = port
        try:
            logger.debug("NETCORE: Attempting to connect to host: %s port: %s",
                         host, port)
            # Set the connect to be a blocking operation
            self.sock.setblocking(True)
            self.sock.connect((self.host, self.port))
            self.sock.setblocking(False)
            self.connected = True
            self.event.emit('net_connect', (self.host, self.port))
            logger.debug("NETCORE: Connected to host: %s port: %s", host, port)
        except socket.error as error:
            logger.error("NETCORE: Error on Connect")
            self.event.emit('SOCKET_ERR', error)

    def set_proto_state(self, state):
        self.proto_state = state
        self.event.emit(proto.state_lookup[state] + '_STATE')

    def set_comp_state(self, threshold):
        self.comp_threshold = threshold
        if threshold >= 0:
            self.comp_state = proto.PROTO_COMP_ON

    def push(self, packet):
        data = packet.encode(self.comp_state, self.comp_threshold)
        self.sbuff += (self.cipher.encrypt(data) if self.encrypted else data)
        self.event.emit(packet.ident, packet)
        self.event.emit(packet.str_ident, packet)
        self.sock.sending = True

    def push_packet(self, ident, data):
        self.push(mcpacket.Packet(ident, data))

    def read_packet(self, data=b''):
        self.rbuff.append(
            self.cipher.decrypt(data) if self.encrypted else data)
        while self.rbuff:
            self.rbuff.save()
            try:
                packet = mcpacket.Packet(ident=(
                    self.proto_state,
                    proto.SERVER_TO_CLIENT
                )).decode(self.rbuff, self.comp_state)
            except BufferUnderflowException:
                self.rbuff.revert()
                break
            except mcpacket.PacketDecodeFailure as err:
                logger.warning('NETCORE: Packet decode failed')
                logger.warning(
                    'NETCORE: Failed packet ident is probably: %s',
                    err.packet.str_ident
                )
                self.event.emit('PACKET_ERR', err)
                break
            self.event.emit(packet.ident, packet)
            self.event.emit(packet.str_ident, packet)

    def enable_crypto(self, secret_key):
        self.cipher = AESCipher(secret_key)
        self.encrypted = True

    def disable_crypto(self):
        self.cipher = None
        self.encrypted = False

    def reset(self, sock):
        self.__init__(sock, self.event)


@pl_announce('Net')
class NetPlugin(PluginBase):
    requires = ('Event', 'Timers')
    defaults = {
        'bufsize': 4096,
        'sock_quit': True,
    }
    events = {
        'event_tick': 'tick',
        'SOCKET_RECV': 'handle_recv',
        'SOCKET_SEND': 'handle_send',
        'SOCKET_ERR': 'handle_err',
        'SOCKET_HUP': 'handle_hup',
        'PLAY<Disconnect': 'handle_disconnect',
        'LOGIN<Disconnect': 'handle_login_disconnect',
        'HANDSHAKE>Handshake': 'handle_handshake',
        'LOGIN<Login Success': 'handle_login_success',
        'LOGIN<Set Compression': 'handle_comp',
        'PLAY<Set Compression': 'handle_comp',
        'event_kill': 'handle_kill',
    }

    def __init__(self, ploader, settings):
        super(NetPlugin, self).__init__(ploader, settings)
        self.bufsize = self.settings['bufsize']
        self.sock_quit = self.settings['sock_quit']
        self.sock = SelectSocket(self.timers)
        self.net = NetCore(self.sock, self.event)
        self.sock_dead = False
        ploader.provides('Net', self.net)

    def tick(self, name, data):
        if self.net.connected:
            for flag in self.sock.poll():
                self.event.emit(flag)
        else:
            timeout = self.timers.get_timeout()
            if timeout == -1:
                time.sleep(1)
            else:
                time.sleep(timeout)

    # SOCKET_RECV - Socket is ready to recieve data
    def handle_recv(self, name, data):
        if self.net.connected:
            try:
                data = self.sock.recv(self.bufsize)
                if not data:
                    self.event.emit('SOCKET_HUP')
                    return
                self.net.read_packet(data)
            except socket.error as error:
                self.event.emit('SOCKET_ERR', error)

    # SOCKET_SEND - Socket is ready to send data and Send buffer contains
    # data to send
    def handle_send(self, name, data):
        if self.net.connected:
            try:
                sent = self.sock.send(self.net.sbuff)
                self.net.sbuff = self.net.sbuff[sent:]
                if self.net.sbuff:
                    self.sock.sending = True
            except socket.error as error:
                self.event.emit('SOCKET_ERR', error)

    # SOCKET_ERR - Socket Error has occured
    def handle_err(self, name, data):
        self.sock.close()
        self.sock = SelectSocket(self.timers)
        self.net.reset(self.sock)
        logger.error("NETPLUGIN: Socket Error: %s", data)
        self.event.emit('net_disconnect', data)
        if self.sock_quit and not self.event.kill_event:
            self.sock_dead = True
            self.event.kill()

    # SOCKET_HUP - Socket has hung up
    def handle_hup(self, name, data):
        self.sock.close()
        self.sock = SelectSocket(self.timers)
        self.net.reset(self.sock)
        logger.error("NETPLUGIN: Socket has hung up")
        self.event.emit('net_disconnect', "Socket Hung Up")
        if self.sock_quit and not self.event.kill_event:
            self.sock_dead = True
            self.event.kill()

    # Handshake - Change to whatever the next state is going to be
    def handle_handshake(self, name, packet):
        self.net.set_proto_state(packet.data['next_state'])

    # Login Success - Change to Play state
    def handle_login_success(self, name, packet):
        self.net.set_proto_state(proto.PLAY_STATE)

    # Handle Set Compression packets
    def handle_comp(self, name, packet):
        self.net.set_comp_state(packet.data['threshold'])

    def handle_disconnect(self, name, packet):
        logger.debug("NETPLUGIN: Disconnected: %s", packet.data['reason'])
        self.event.emit('net_disconnect', packet.data['reason'])

    def handle_login_disconnect(self, name, packet):

        reason = packet.data.get('json_data', {}).get('text', '???')

        logger.debug("NETPLUGIN: Disconnected: %s", reason)
        self.event.emit('net_disconnect', reason)

    # Kill event - Try to shutdown the socket politely
    def handle_kill(self, name, data):
        if self.net.connected:
            logger.debug("NETPLUGIN: Kill event received, closing socket")
            if not self.sock_dead:
                self.sock.shutdown(socket.SHUT_WR)
            self.sock.close()
