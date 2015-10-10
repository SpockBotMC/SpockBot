class BufferUnderflowException(Exception):
    pass


class BoundBuffer(object):
    buff = b''
    cursor = 0

    def __init__(self, data=b""):
        self.write(data)

    def read(self, length):
        if length > len(self):
            raise BufferUnderflowException()

        out = self.buff[self.cursor:self.cursor+length]
        self.cursor += length
        return out

    def write(self, data):
        self.buff += data

    def flush(self):
        return self.read(len(self))

    def save(self):
        self.buff = self.buff[self.cursor:]
        self.cursor = 0

    def revert(self):
        self.cursor = 0

    def tell(self):
        return self.cursor

    def __len__(self):
        return len(self.buff) - self.cursor

    def __repr__(self):
        return "<BoundBuffer '%s'>" % repr(self.buff[self.cursor:])

    recv = read
    append = write
