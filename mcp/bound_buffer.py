class BufferUnderflowException(Exception):
    pass

class BoundBuffer:
    backup = ''
    def __init__(self, *args):
        self.buff = (args[0] if args else '')
    
    def read(self, bytes):
        if len(self.buff) < bytes:
            raise BufferUnderflowException()
        o, self.buff = self.buff[:bytes], self.buff[bytes:]
        return o

    def append(self, bytes):
        self.buff += bytes
    
    def flush(self):
        out = self.buff
        self.buff = ''
        self.save()
        return out
    
    def save(self):
        self.backup = str(self.buff)
    
    def revert(self):
        self.buff = str(self.backup)
    
    recv = read