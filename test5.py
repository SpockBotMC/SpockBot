from mcp.utils import ByteToHex
from mcp import datautils

char = "LOL THIS IS A STRING".encode("utf-8")

print ByteToHex(char)
data = datautils.EncodeData(char, 'string')
print ByteToHex(data)
print data
print datautils.DecodeData(data, 'string')[0]