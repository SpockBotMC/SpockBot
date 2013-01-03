from nbt import nbt
from mcp.bound_buffer import BoundBuffer
from mcp.datautils import DecodeData
from mcp.utils import ByteToHex
from gzip import GzipFile
from StringIO import StringIO

magic = open('bigtest.nbt').read()

blarg = GzipFile(fileobj = StringIO(magic))
herro = blarg.read()
print herro
print ByteToHex(herro)
blarg.close()


bbuf=BoundBuffer()
bbuf.append(herro)


def decompress(s):
    f = gzip.GzipFile(fileobj=StringIO(s))
    o = f.read()
    f.close()
    return o

nbtfile = nbt.NBTFile(buffer = bbuf)
print nbtfile.pretty_tree()