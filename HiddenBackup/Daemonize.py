import atexit
import os
import pwd
import sys
import time
from BaseHTTPServer import HTTPServer
from signal import SIGTERM

from HiddenBackup.BackupThread import BackupThread
from HiddenBackup.ConfigLoader import Config
from HiddenBackup.HiddenService import HiddenService
from HiddenBackup.LogWriter import Logger


class Daemonize:
    _pidfile = '/var/run/HDBackup.pid'
    _stdin = '/dev/null'
    _stdout = '/dev/null'
    _stderr = '/dev/null'
    _log = None
    _config = None
    _hs = None
    _server = None

    def __init__(self):
        self._log = Logger()
        self._config = Config()
        self._hs = HiddenService(self._log, self._config.local_port(), self._config.tor_port())

    def daemonize(self):
        # close log at exit
        atexit.register(self._log.close)

        # do the UNIX double-fork magic
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError, e:
            self._log.error("fork #1 failed: %d (%s)" % (e.errno, e.strerror))
            sys.exit(1)

        # decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)

        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError, e:
            self._log.error("fork #2 failed: %d (%s)" % (e.errno, e.strerror))
            sys.exit(1)

        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = file(self._stdin, 'r')
        so = file(self._stdout, 'a+')
        se = file(self._stderr, 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # get user data
        try:
            user = pwd.getpwnam(self._config.run_as())
        except KeyError:
            self._log.error("user does not exists: %s" % self._config.run_as())
            sys.exit(1)

        # write pidfile
        atexit.register(self.delpid)
        pid = str(os.getpid())
        file(self._pidfile, 'w+').write("%s\n" % pid)
        os.chown(self._pidfile, user[2], user[3])

        # Change process uid
        os.setuid(user[2])

    def delpid(self):
        os.remove(self._pidfile)

    def start(self):
        """
        Start the daemon
        """

        # Check for a pidfile to see if the daemon already runs
        try:
            pf = file(self._pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if pid:
            message = "pidfile %s already exist. Daemon already running?\n"
            self._log.error(message % self._pidfile)
            sys.exit(1)

        # Start the daemon
        self.daemonize()
        self.run()

    def stop(self):
        """
        Stop the daemon
        """
        # Get the pid from the pidfile
        try:
            pf = file(self._pidfile, 'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if not pid:
            message = "pidfile %s does not exist. Daemon not running?\n"
            self._log.error(message % self._pidfile)
            return  # not an error in a restart

        # Remove hidden services from tor
        if self._hs.connect(self._config.server_password()):
            self._hs.unbind()

        # Try killing the daemon process
        try:
            while 1:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
        except OSError, err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self._pidfile):
                    os.remove(self._pidfile)
            else:
                print str(err)
                sys.exit(1)

    def restart(self):
        """
        Restart the daemon
        """
        self.stop()
        self.start()

    def run(self):
        # Start hidden services
        if not self._hs.connect(self._config.server_password()):
            self._log.error("There was an error when trying connect to Tor daemon")
            sys.exit(1)
        self._hs.bind()

        # Run backup server
        try:
            self._server = HTTPServer(('127.0.0.1', self._config.local_port()), BackupThread)
            # Wait forever for incoming htto requests
            self._server.serve_forever()
        except:
            self._log.error("There was an error when trying to bind the server")
            exit(2)
