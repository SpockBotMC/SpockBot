from mcp import nbt
from mcp.bound_buffer import BoundBuffer

magic = open('bigtest.nbt').read()

bbuf=BoundBuffer()
bbuf.append(magic)

print nbt.read_nbt(bbuf, len(magic)).pretty_tree()