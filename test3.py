from mcp import nbt
from mcp.bound_buffer import BoundBuffer

magic = open('bigtest.nbt').read()

bbuf=BoundBuffer()
bbuf.append(magic)

tags = nbt.read_nbt(bbuf, len(magic))
print tags.pretty_tree()