try:
    basestring
except NameError:
    basestring = str

import copy
import logging
import zlib
from time import gmtime, strftime

from spockbot.mcp import datautils, proto
from spockbot.mcp.bbuff import BoundBuffer, BufferUnderflowException
from spockbot.mcp.extensions import hashed_extensions
from spockbot.mcp.proto import MC_VARINT


logger = logging.getLogger('spockbot')


class PacketDecodeFailure(Exception):
    def __init__(self, packet, pbuff, underflow=False):
        self.packet = packet
        self.pbuff = pbuff
        self.underflow = underflow


class Packet(object):
    def __init__(self,
                 ident=[proto.HANDSHAKE_STATE, proto.CLIENT_TO_SERVER, 0x00],
                 data=None
                 ):
        if isinstance(ident, basestring):
            ident = proto.packet_str2ident[ident]
        self.__ident = list(ident)
        # Quick hack to fake default ident
        if len(self.__ident) == 2:
            self.__ident.append(0x00)
        self.ident = tuple(self.__ident)
        self.str_ident = proto.packet_ident2str[self.ident]
        self.data = data if data else {}

    def clone(self):
        return Packet(self.ident, copy.deepcopy(self.data))

    def new_ident(self, ident):
        self.__init__(ident, self.data)

    def decode(self, bbuff, proto_comp_state):
        self.data = {}
        packet_length = datautils.unpack(MC_VARINT, bbuff)
        packet_data = bbuff.recv(packet_length)
        pbuff = BoundBuffer(packet_data)
        if proto_comp_state == proto.PROTO_COMP_ON:
            body_length = datautils.unpack(MC_VARINT, pbuff)
            if body_length:
                body_data = zlib.decompress(pbuff.flush(), zlib.MAX_WBITS)
                pbuff.write(body_data)
                pbuff.save()

        try:
            # Ident
            self.__ident[2] = datautils.unpack(MC_VARINT, pbuff)
            self.ident = tuple(self.__ident)
            self.str_ident = proto.packet_ident2str[self.ident]
            # Payload
            for dtype, name in proto.hashed_structs[self.ident]:
                self.data[name] = datautils.unpack(dtype, pbuff)
            # Extension
            if self.ident in hashed_extensions:
                hashed_extensions[self.ident].decode_extra(self, pbuff)
            if pbuff:
                raise PacketDecodeFailure(self, pbuff)
        except BufferUnderflowException:
            raise PacketDecodeFailure(self, pbuff, True)
        return self

    def encode(self, proto_comp_state, proto_comp_threshold, comp_level=6):
        # Ident
        o = datautils.pack(MC_VARINT, self.ident[2])
        # Payload
        for dtype, name in proto.hashed_structs[self.ident]:
            o += datautils.pack(dtype, self.data[name])
        # Extension
        if self.ident in hashed_extensions:
            o += hashed_extensions[self.ident].encode_extra(self)

        if proto_comp_state == proto.PROTO_COMP_ON:
            uncompressed_len = len(o)
            if uncompressed_len < proto_comp_threshold:
                header = datautils.pack(MC_VARINT, uncompressed_len + 1)
                header += datautils.pack(MC_VARINT, 0)
            else:
                o = zlib.compress(o, comp_level)
                ulen_varint = datautils.pack(MC_VARINT, uncompressed_len)
                header = datautils.pack(MC_VARINT,
                                        len(o) + len(ulen_varint))
                header += ulen_varint
            return header + o
        elif proto_comp_state == proto.PROTO_COMP_OFF:
            return datautils.pack(MC_VARINT, len(o)) + o
        else:
            return None

    def __repr__(self):
        s = ('<<<', '>>>')[self.ident[1]]
        f = "[%s] %s (0x%02X, 0x%02X): %-" + str(
            max([len(i) for i in proto.hashed_names.values()]) + 1) + "s%s"
        return f % (
            strftime("%H:%M:%S", gmtime()), s, self.ident[0], self.ident[2],
            proto.hashed_names[self.ident],
            str(self.data)
        )
