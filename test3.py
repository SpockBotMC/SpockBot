from mcp import nbt
from mcp.bound_buffer import BoundBuffer
from StringIO import StringIO
import gzip
from mcp.utils import ByteToHex

magic = open('bigtest.nbt').read()

print ByteToHex(magic)



tags = nbt.decode_nbt(magic)
foo = nbt.encode_nbt(tags)

gzipstring = StringIO()
blarg = gzip.GzipFile(fileobj = gzipstring, mode = 'wb')

blarg.write(foo)
blarg.close()
print "lol"
print ByteToHex(gzipstring.getvalue())