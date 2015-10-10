from spockbot.mcp import datautils


def test_unpack_varint():
    largebuff = datautils.BoundBuffer(b'\x80\x94\xeb\xdc\x03')
    smallbuff = datautils.BoundBuffer(b'\x14')
    assert datautils.unpack_varint(smallbuff) == 20
    assert datautils.unpack_varint(largebuff) == 1000000000


def test_pack_varint():
    assert datautils.pack_varint(20) == b'\x14'
    assert datautils.pack_varint(1000000000) == b'\x80\x94\xeb\xdc\x03'
    assert datautils.pack_varint(-10000000000) is None
    assert datautils.pack_varint(10000000000) is None


def test_unpack_varlong():
    largebuff = datautils.BoundBuffer(b'\x80\xc8\xaf\xa0%')
    smallbuff = datautils.BoundBuffer(b'\x14')
    assert datautils.unpack_varlong(smallbuff) == 20
    assert datautils.unpack_varlong(largebuff) == 10000000000


def test_pack_varlong():
    assert datautils.pack_varlong(20) == b'\x14'
    assert datautils.pack_varlong(10000000000) == b'\x80\xc8\xaf\xa0%'
    assert datautils.pack_varlong(10000000000000000000) is None
    assert datautils.pack_varlong(-10000000000000000000) is None
