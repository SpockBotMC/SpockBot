from mcp import nbt
from mcp.bound_buffer import BoundBuffer

magic = open('bigtest.nbt').read()

tags = nbt.decode_nbt(magic)
foo = nbt.encode_nbt(tags)
tags = nbt.decode_nbt(foo, False)
print tags.pretty_tree()