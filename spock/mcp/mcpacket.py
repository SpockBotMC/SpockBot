import copy
import zlib
from time import gmtime, strftime
from spock import utils
from spock.mcp import datautils, mcdata
from spock.mcp.mcpacket_extensions import hashed_extensions
from spock.mcp.mcdata import (
    MC_BOOL, MC_UBYTE, MC_BYTE, MC_USHORT, MC_SHORT, MC_UINT, MC_INT, MC_ULONG,
    MC_LONG, MC_FLOAT, MC_DOUBLE, MC_VARINT, MC_VARLONG, MC_FP_INT, MC_FP_BYTE,
    MC_UUID, MC_POSITION, MC_STRING, MC_CHAT, MC_SLOT, MC_META
)

try:
  basestring
except NameError:
  basestring = str

import logging
logger = logging.getLogger('spock')

class PacketDecodeFailure(Exception):
    def __init__(self, packet, pbuff, underflow = False):
        self.packet = packet
        self.pbuff = pbuff
        self.underflow = underflow

class Packet(object):
    def __init__(self,
        ident = [mcdata.HANDSHAKE_STATE, mcdata.CLIENT_TO_SERVER, 0x00],
        data = None
    ):
        if isinstance(ident, basestring):
            ident = mcdata.packet_str2ident[ident]
        self.__ident = list(ident)
        #Quick hack to fake default ident
        if len(self.__ident) == 2:
            self.__ident.append(0x00)
        self.ident = tuple(self.__ident)
        self.str_ident = mcdata.packet_ident2str[self.ident]
        self.data = data if data else {}

    def clone(self):
        return Packet(self.ident, copy.deepcopy(self.data))

    def new_ident(self, ident):
        self.__init__(ident, self.data)

    def decode(self, bbuff, proto_comp_state):
        self.data = {}
        if proto_comp_state == mcdata.PROTO_COMP_ON:
            packet_length = datautils.unpack(MC_VARINT, bbuff)
            start = bbuff.tell()
            data_length = datautils.unpack(MC_VARINT, bbuff)
            packet_data = bbuff.recv(packet_length-(bbuff.tell()-start))
            if data_length:
                packet_data = zlib.decompress(packet_data, zlib.MAX_WBITS)
        elif proto_comp_state == mcdata.PROTO_COMP_OFF:
            packet_data = bbuff.recv(datautils.unpack(MC_VARINT, bbuff))
        else:
            return None
        pbuff = utils.BoundBuffer(packet_data)

        try:
            #Ident
            self.__ident[2] = datautils.unpack(MC_VARINT, pbuff)
            self.ident = tuple(self.__ident)
            self.str_ident = mcdata.packet_ident2str[self.ident]
            #Payload
            for dtype, name in mcdata.hashed_structs[self.ident]:
                self.data[name] = datautils.unpack(dtype, pbuff)
            #Extension
            if self.ident in hashed_extensions:
                hashed_extensions[self.ident].decode_extra(self, pbuff)
            if pbuff.buff:
                raise PacketDecodeFailure(self, pbuff)
        except utils.BufferUnderflowException:
            raise PacketDecodeFailure(self, pbuff, True)
        return self

    def encode(self, proto_comp_state, proto_comp_threshold, comp_level = 6):
        #Ident
        o = datautils.pack(MC_VARINT, self.ident[2])
        #Payload
        for dtype, name in mcdata.hashed_structs[self.ident]:
            o += datautils.pack(dtype, self.data[name])
        #Extension
        if self.ident in hashed_extensions:
            o += hashed_extensions[self.ident].encode_extra(self)

        if proto_comp_state == mcdata.PROTO_COMP_ON:
            uncompressed_len = len(o)
            if uncompressed_len < proto_comp_threshold:
                header = datautils.pack(MC_VARINT, uncompressed_len + 1)
                header += datautils.pack(MC_VARINT, 0)
            elif uncompressed_len >= proto_comp_threshold:
                o = zlib.compress(o, comp_level)
                ulen_varint = datautils.pack(MC_VARINT, uncompressed_len)
                header = datautils.pack(MC_VARINT, uncompressed_len + len(ulen_varint))
                header += ulen_varint
            return header + o
        elif proto_comp_state == mcdata.PROTO_COMP_OFF:
            return datautils.pack(MC_VARINT, len(o)) + o
        else:
            return None

    def __repr__(self):
        s = ('<<<', '>>>')[self.ident[1]]
        f = "[%s] %s (0x%02X, 0x%02X): %-"+str(max([len(i) for i in mcdata.hashed_names.values()])+1)+"s%s"
        return f % (strftime("%H:%M:%S", gmtime()), s, self.ident[0], self.ident[2], mcdata.hashed_names[self.ident], str(self.data))
