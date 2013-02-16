import sys

from daemon import DaemonClass

from spock.net.client import Client
from plugins import ReConnect, AntiAFK, SkyNet
from login import username, password

SETTINGS = {
    'APP' :     'spockd',
    'PIDFILE' : '/home/nickg/spockd.pid',
    'LOG' :     '/home/nickg/spockd.log',
}

# Subclass the daemon class
class Spock_Daemon(DaemonClass):
	def __init__(self):
		DaemonClass.__init__(self, SETTINGS)

	def run(self):
		plugins = [ReConnect.ReConnectPlugin, AntiAFK.AntiAFKPlugin, SkyNet.SkyNetPlugin]
		client = Client(plugins)
		client.start(username, password, host = 'untamedears.com')
		self.cleanup()


if __name__ == '__main__':
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            sys.stdout.write("Starting the app...\n")
            app = Spock_Daemon()
            sys.stdout.write("Starting daemon mode...")
            app.start()
        elif 'stop' == sys.argv[1]:
            app = Spock_Daemon()
            sys.stdout.write("Stopping the daemon...\n")
            app.stop()
        elif 'restart' == sys.argv[1]:
            app = Spock_Daemon()
            sys.stdout.write("Restarting the daemon...")
            app.restart()
        elif 'status' == sys.argv[1]:
            app = Spock_Daemon()
            app.status()
        else:
            print "usage: %s start|stop|restart/status" % sys.argv[0]
            sys.exit(2)
    else:
            print "Invalid command: %r" % ' '.join(sys.argv)
            print "usage: %s start|stop|restart|status" % sys.argv[0]
            sys.exit(2)

    print "...Done"