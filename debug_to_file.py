#!/usr/bin/env python

"""
    Creates a writeable file-like object
    Useful for logging redirected stdout and stderr

    v0.  21 April 2012
"""

# Std Python Modules
import os, datetime


class DebugToFileClass:
    """
        File-like object
        All print statements used for debugging can be redirected to this file
    """
    def __init__(self, filename, appname, tag=None, overwrite=True):
        self.filename = filename
        self.appname = appname
        self.tag = tag
        if os.path.exists(self.filename):
            if overwrite:
                os.remove(self.filename)
            now = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
            self.write("Logging started at %s ----" % now)
        else:
            # This will generate an error
            pass

    def write(self, msg):
        try:
            f = open(self.filename,'a')
            f.writelines(datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S') + ': ' + self.appname + ': ' + self.tag + ': ' + msg.strip() + '\n')
            f.flush()
            f.close()
        except:
            pass

if __name__ == '__main__':
    # Test
    import platform

    if platform.system() == 'Linux':
        filename = '/home/Daemon/test.log'
    elif platform.system() == 'Windows':
        filename = 'H:\\Daemon\\test.log'
    else:
        filename = 'test.log'

    d = DebugToFileClass(tag='TEST', filename=filename, appname="My App", overwrite=True)
    d.write(msg='Hello World')
