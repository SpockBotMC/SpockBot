#!/usr/bin/python

"""
    A simple class to daemonise a Python programme
    Starts, Stops, Restarts, Gets Status for a Linux Daemon

    Usage:
        1. Subclass DaemonClass
        
        2. Override methods as required, typically:
            run()           # Place your functionality in this method. Must contain a continuous loop or blocking function call
            on_exit()       # Additional Clean up tasks just before the daemon exits
            on_interrupt()  # Additional tasks when a SIGTERM or SIGINT signal is received
            
        3. You may also want to override the follow methods for any processing required before the event is triggered
            before_start()
            before_stop()
            before_restart()
            
        4. Run from the command line:
            python daemon.py start
            python daemon.py stop
            python daemon.py restart
            python daemon.py status
            
        5. If required, create:
            An init script so the daemon starts when the server boots
            Or a cron job to start at boot or start/stop/restart at specific times/days

    Example:
        See the separate example which daemonises a simple web server
        
    Requires/Dependencies
        Python 2.x
        No other dependencies
    
    OS (tested):
        Linux (any flavour)
        Windows 7 (will run in the foreground, not as a Windows service - to be implemented in the future)
    
    Key References:
        Based heavily on a post and comments at
            http://www.jejik.com/articles/2007/02/a_simple_unix_linux_daemon_in_python/
        How to Daemonize in Linux by Doug Potter, http://www-theorie.physik.unizh.ch/~dpotter/howto/daemonize
        Advanced Programming in the Unix Environment by W. Richard Stevens, ISBN 9780201563177
        http://en.wikipedia.org/wiki/Umask
        http://en.wikipedia.org/wiki/Process_group

    Andrew Cuddon
    http://www.cuddon.net/2013/01/a-linux-daemon-written-in-python.html
    v1.0  21 January 2013
"""

# Std Python Modules
import sys, os, signal, platform
import datetime, time

# App Modules
from debug_to_file import DebugToFileClass

__version__ = '1.0'


class DaemonClass:
    """
        Usage:
            Subclass this class and and override run(), tidyup() and son_interrupt() methods (See the example/test below
    """
    # Default directory for the running daemon. Set to something harmess
    DEFAULT_DIRECTORY_LINUX = '/tmp'
    DEFAULT_DIRECTORY_WINDOWS = 'C:\\temp'
    DEFAULT_DIRECTORY_OTHER = ''
    
    OVERWRITE_LOG = False

    def __init__(self, settings=None):
        """
            Initialises the class
            settings is a dict, e.g. for Linux:
                settings = {'APP' : 'mydaemon',  'PIDFILE' : '/home/andrew/Documents/Development/Daemon/mydaemon.pid',  'LOG' : '/home/andrew/Documents/Development/Daemon/mydaemon.log'}
            Full pathnames are required in the settings since the daemon has no knowledge of the current folder
        """
        self.settings = settings
        self.platform = platform.system()   # 'Linux', 'Windows' etc
        self.alive = True

        # Null device for redirecting input and output
        if (hasattr(os, "devnull")):
            DEVNULL = os.devnull
        else:
            DEVNULL = "/dev/null"
        self.stdin = DEVNULL
        self.stdout = DEVNULL
        self.stderr = DEVNULL

        # Pathfilname of the pid file (Process ID file)
        self.pidfile = self.settings['PIDFILE']
        # Get the pid of the current process (not yet daemonized)
        self.pid = os.getpid()

        # Register the signal handlers so we can exit gracefully when a signal is received
        signal.signal(signal.SIGTERM, self.signal_handler)      # Terminate Signal (on daemon stop, system shutdown etc)
        signal.signal(signal.SIGINT, self.signal_handler)       # Interrupt Signal (ctrl-c etc)

        # signaltrapped is True when the first signal has been trapped. Stops the same signal being trapped multiple times.
        self.signaltrapped = False

    def set_mode(self, mode):
        # Mode is one of ['starting', 'stopping', 'restarting', 'daemonised', 'foreground']
        self.mode = mode
        sys.stdout.write('Mode set to: %s\n' % mode)
        
    def get_mode(self):
        return self.mode

    #-----------------------------------------------------------------------------------
    # START
    #-----------------------------------------------------------------------------------
    def before_start(self):
        """
            Override this method if you need to do something before the daemon/service STARTS
        """
        pass

    def start(self):
        """
            START the daemon/service
        """
        self.set_mode('starting')
        self.before_start()  # Pre-start processing
        
        if self.platform == "Linux":
            ## Linux Daemon
            
            sys.stdout.write("Checking whether the Linux Daemon is already running()...\n")
            # Check for a pidfile (Process ID file) to see if the daemon is already running
            if os.path.exists(self.pidfile):
                try:
                    pf = file(self.pidfile,'r')
                    self.pid = int(pf.read().strip())
                    pf.close()
                    # exit if the pid file already exists. Presumably there is already an instance running.
                    sys.stderr.write("pidfile %s already exists. The Daemon already running with process ID: %r\n" % (self.pidfile,  self.pid))
                    sys.exit(1)
                except IOError:
                    # error opening the pid file
                    sys.stderr.write("Error opening pidfile: %s. You may need to delete it mannually and possibly manually kill the process\n" % self.pidfile)
                    sys.exit(1)
                    self.pid = None
            else:
                # No PID file so the daemon is NOT currently running
                self.pid = os.getpid()

            # No existing daemon process so we can now demonise the current process
            # Start the daemon
            self.start_linux_daemon()
        elif self.platform == "Windows":
            ## Windows Service
            start_windows_service()
        else:
            # Other platforms run non demonised
            sys.stdout.write("Daemon mode not supported on %s OS, so running non-demonised...\n" % self.platform)
        
        # Start processing in the background
        self.run()

    def start_linux_daemon(self):
        """
            Decouple from the original environment and create the Linux_daemon
        """
        sys.stdout.write("Daemonising the current process...\n")

        # Fork the current process. This creates an exact copy of the original so there are two instances running
        # fork() retuns a positive pid for the parent process and a zero pid for the child process
        # The actual pid of the child process can be retrieved afterwards via os.getpid() (it will be non-zero)
        try:
            pid = os.fork()
            if pid > 0:
                # This is the parent process so just exit gracefully
                time.sleep(0.1)
                sys.exit(0)
                # Now only the CHILD process is running
        except OSError, e:
            sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        # Only the CHILD process continues on from here
        self.pid = os.getpid()

        # Set the daemon's default directory/folder to something harmless
        os.chdir(self.DEFAULT_DIRECTORY_LINUX)

        # Relinquish any elevated priviledges
        # Create a new session containing a single (new) process group
        # A process group is a collection of one or more processes. Process groups are used to control the distribution of signals (SIGTERM, SIGINT etc).
        os.setsid()

        # Set file permissions for newly created files
        # The child processes inherit the mask from the parent (and originally the terminal from where the command was run)
        # Set the process's umask to let the operating system determine the file permissions)
        # see http://en.wikipedia.org/wiki/Umask
        os.umask(0)

        # Do second fork to really distance us form the original process
        try:
            pid = os.fork()
            if pid > 0:
                # This is the CHILD process so exit gracefully
                time.sleep(0.1)
                sys.exit(0)
                # Now only the GRANDCHILD process is running
        except OSError, e:
            sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        # Only the GRANDCHILD process continues on from here
        # This is the running daemon process
        # Get the pid number
        self.pid = os.getpid()

        # Redirect std out and std error to writable object for debugging/Logging (a daemon should not write to stdout/err)
        sys.stdout.flush()
        sys.stderr.flush()
        self.so = DebugToFileClass(tag='STDOUT',  filename=self.settings['LOG'], appname=self.settings['APP'], overwrite=self.OVERWRITE_LOG)
        self.se = DebugToFileClass(tag='STDERR', filename=self.settings['LOG'], appname=self.settings['APP'], overwrite=False)
        sys.stdout = self.so
        sys.stderr = self.se

        # Save a pidfile for the current process (which is the grandchild of the original process)
        # The pid file is used to check whether a process is already running and could be used for interprocess communication
        sys.stdout.write("**** The PROCESS ID for the RUNNING DAEMON is: %s  ****\n" % str(os.getpid()))
        file(self.pidfile,'w+').write("%s\n" % str(os.getpid()))
        self.set_mode('daemonized')

    def start_windows_service(self):
        """
            Not implemented
        """
        # Window service not yet implemented
        sys.stdout.write("%s process mode not yet implemented, so running in the foreground...\n" % self.platform)

        if self.platform == "Windows":
            os.chdir(self.DEFAULT_DIRECTORY_WINDOWS)
        self.set_mode('foreground')

    #-----------------------------------------------------------------------------------
    # STOP
    #-----------------------------------------------------------------------------------
    def before_stop(self):
        """
            Override this method if you need to do something before the daemon/service STOPS
        """
        pass
    
    def stop(self):
        """
            STOP the daemon/service
            Stops the original daemon and creates a new daemon, enabling configuration changes to be reloaded
        """
        self.set_mode('stopping')
        self.before_stop()  # Pre-stop processing

        if self.platform == "Linux":
            self.stop_linux_daemon()
        elif self.platform == "Windows":
            self.stop_windows_service()
        else:
            return

    def stop_linux_daemon(self):
        """
            Terminates the daemon running in another process (by issuing a SIGTERM - terminate signal)
            This will be issued only by a second instance such as from the command line, e.g.:
                mydaemon.py stop
            The daemon being terminated will trap the signal and exit gracefully.
        """
        sys.stdout.write("(PID: %s) mydaemon.py stop: DaemonClass.stop()...\n" % self.pid)

        pid = self.status()

        if not pid:
            sys.stderr.write(" * Daemon is not running so cannot stop it.\n")
            return

        # Try shutting down the daemon process
        sys.stdout.write("...Sending SIGTERM to process %s\n" % pid)
        try:
            # Send a terminate signal to the daemon process
            os.kill(pid, signal.SIGTERM)        # This gets trapped by signal_handler() in the daemon being terminated
            time.sleep(0.1)
        except OSError, err:
            err = str(err)
            if err.find("No such process") > 0:
                # The process identified by the pid file does not exit
                # So just remove the pid file
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                sys.stderr.write(str(err))
                sys.exit(1)

        # Now exit the instance that invoked the stop()
        if self.mode == 'stop':
            sys.exit(0)       # Note: we do not want to exit when we are doing a restart

    def stop_windows_service(self):
        sys.stdout.write("Windows service functionality not yet implemented\n" % self.pid)

    #-----------------------------------------------------------------------------------
    # RESTART
    #-----------------------------------------------------------------------------------
    def before_restart(self):
        """
            Override this method if you need to do something before the daemon/service RESTARTS
            Restart notes:
                before_stop() and before_start() are also triggered when restarting the daemon
                before_stop() will be triggered on the daemonised processes
                before_start() will be triggered on the current process (which will become the new dameon)
        """
        pass

    def restart(self):
        """
            RESTART the daemon/service
            Stops the original daemon and creates a new daemon, enabling configuration changes to be reloaded
        """
        self.set_mode('restarting')
        self.before_restart()
        
        if self.platform == "Linux":
            sys.stdout.write("(PID: %s) Restarting the Linux Daemon...\n")
            self.stop_linux_daemon()          # Stops the original daemon process by issuing a SIGTERM
            self.start_linux_daemon()         # Starts a new daemon in the current process
        elif self.platform == "Windows":
            self.stop_windows_service()
            self.start_windows_service()
        else:
            pass
        
        self.run()                  # Passes processing control to the run method

    #-----------------------------------------------------------------------------------
    # STATUS
    #-----------------------------------------------------------------------------------
    def status(self):
        """
            Print the daemon/service status (running or not)
            Return the pid
        """
        if self.platform == "Linux":
            message = ""
            # Get the pid of the running daemon (not the current process) from the pidfile
            if os.path.exists(self.pidfile):
                try:
                    pf = file(self.pidfile,'r')
                    pid = int(pf.read().strip())
                    pf.close()
                    message = " * %s is running (Process ID = %s)\n" % (self.settings['APP'], pid)
                except IOError:
                    message = " * %s is running (but can't read the pid file)\n" % (self.settings['APP'],)
                    pid = None
            else:
                message = " * %s IS NOT running (no PID file)\n" % (self.settings['APP'],)
                pid = None

            sys.stdout.write(message)
            return pid
        elif self.platform == "Windows":
            sys.stdout.write("Windows Service not yet implemented...\n")
            return None
        else:
            sys.stdout.write("Daemon mode not currently supported on %s OS, so running non-demonised...\n" % self.platform)
            return None

    #-----------------------------------------------------------------------------------
    # Process/Run
    #-----------------------------------------------------------------------------------
    def run(self):
        """
            This is where your processing occurs
            This must be a continuous look or the daemon will exit once processing has finished
            The loop finished when an interrupt signal is received and 'alive' is set to False

            Override this method when you subclass Daemon. It will be called after the process has been daemonized by start() or restart().
        """
        sys.stdout.write('Starting Processing (pid:%s)...\n'  % self.pid)

        i = 1
        while self.alive:
            # Do something. In this case just write a line of text and wait for 1 second, then do it all over again
            sys.stdout.write('%d: Daemon/Service is running with a process id (pid) = %s\n' % (i, self.pid))
            i+=1
            try:
                time.sleep(1)
            except:
                # traps and ignores any error if an interrupt is received while sleeping/waiting
                pass
        sys.stdout.write('...Procesing has ended.\n')
        self.on_exit()
        self.cleanup()

    #-----------------------------------------------------------------------------------
    # CLOSE
    #-----------------------------------------------------------------------------------
    def on_exit(self):
        """
            Override this method for any additional clean up processing just before the daemon exits
        """
        pass

    def cleanup(self):
        """
            Cleanup, ensures graceful exit
        """
        sys.stdout.write('Cleaning up...')
        
        # Delete the PID file
        if os.path.exists(self.pidfile):
            sys.stdout.write('Deleting the PID file\n')
            os.remove(self.pidfile)
        else:
            sys.stdout.write('PID file does not exist so no need to deleted it\n')

        # Reset stdout and stderr to the terminal
        sys.stdout.write("Resetting STDOUT and STDERR to the terminal...\n")
        sys.stdout.write("..All Done")
        sys.stdout = sys.__stdout__         # reset std out
        sys.stderr = sys.__stderr__         # reset std err
        
        sys.exit(0)

    def signal_handler(self, signum, frame):
        """
            Traps a SIGTERM or SIGINT and exits gracefully
            see __init__() for how this handler is set
            Scenarios:
                SIGTERM issued by the system just prior to a shutdown or restart
                SIGTERM generated by a stop() from a second command line instance (e.g. mydaemon.py stop)
                SIGNTERM issued by a user initiated 'kill process' from the Gnome System Monitor
                Ctr-C/Ctrl-Break by a user (less likely because the daemon detaches from ther terminal
        """
        signals = {15:'SIGTERM (TERMinate SIGnal)',  2: 'SIGINT (INTerupt (Ctrl-C) SIGnal)'}

        sys.stdout.write("(pid:%s) DaemonClass.signal_handler(): %s received\n" % (self.pid, signals[signum]))

        if not self.signaltrapped:
            sys.stdout.write("(pid:%s) DaemonClass.signal_handler()...External signal received so quitting gracefully.\n" % self.pid)

        self.alive = False
        self.signaltrapped = True       # To stop the signal being tapped multiple times

        # Quit gracefully
        self.on_interrupt()

    def on_interrupt(self):
        """
            Subclass this
        """
        pass


if __name__ == '__main__':
    # Testing Only
    # The Daemon class should be subclassed and the run(), tidyup() and on_interrupt() methods overridden
    app = None

    if platform.system() == 'Linux':
        # Full path names are required because the daemon has no knowledge of the current directory/folder
        SETTINGS = {
            'APP' : 'mydaemon',
            'PIDFILE' : '/home/Daemon/mydaemon.pid',
            'LOG' : '/home/Daemon/mydaemon.log'
        }
    elif platform.system() == 'Windows':
        SETTINGS = {
            'APP' : 'mydaemon',
            'PIDFILE' : 'H:\\Daemon\\mydaemon.pid',
            'LOG' : 'H:\\Daemon\\mydaemon.log'
        }
    else:
        SETTINGS = {
            'APP' : 'mydaemon',
            'PIDFILE' : 'mydaemon.pid',
            'LOG' : 'mydaemon.log'
        }

    print "\n----- %s (Release: %s) -----" % (SETTINGS['APP'],  __version__)

    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            print "Preparing the daemon.."
            app = DaemonClass(SETTINGS)
            print "Starting daemon mode..."
            app.start()
        elif 'stop' == sys.argv[1]:
            app = DaemonClass(SETTINGS)
            print "Stopping the daemon..."
            app.stop()
        elif 'restart' == sys.argv[1]:
            app = DaemonClass(SETTINGS)
            print "Restarting the daemon..."
            app.restart()
        elif 'status' == sys.argv[1]:
            app = DaemonClass(SETTINGS)
            app.status()
        else:
            print "usage: %s start|stop|restart/status" % sys.argv[0]
            sys.exit(2)
    else:
        print "Invalid command: %r" % ' '.join(sys.argv)
        print "usage: %s start|stop|restart|status\n\n" % sys.argv[0]
        sys.exit(2)


# End of module
