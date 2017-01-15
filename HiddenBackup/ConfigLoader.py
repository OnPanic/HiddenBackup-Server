import ConfigParser
from sys import exit


class Config:
    _config_file = '/etc/hiddenbackupd.conf'

    _local_port = None
    _tor_port = None
    _run_as = None
    _server_password = None
    _auth_cookie = None
    _backup_dir = None

    def __init__(self):
        try:
            config = ConfigParser.ConfigParser()
            config.readfp(open(self._config_file))
            self._challenge_port = config.getint('network', 'local_port')
            self._challenge_port = config.getint('network', 'tor_port')
            self._server_password = config.get('tor', 'tor_password')
            self._auth_cookie = config.get('tor', 'auth_cookie')
            self._run_as = config.get('system', 'run_as')
            self._backup_dir = config.get('system', 'backup_dir')
        except ConfigParser.NoOptionError:
            print "Error reading config file."
            exit(2)

    def server_password(self):
        return self._server_password

    def local_port(self):
        return self._local_port

    def tor_port(self):
        return self._tor_port

    def run_as(self):
        return self._run_as

    def auth_cookie(self):
        return self._auth_cookie

    def backup_dir(self):
        return self._backup_dir
