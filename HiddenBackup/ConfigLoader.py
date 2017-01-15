import ConfigParser
import json
from sys import exit


class Config:
    _config_file = '/etc/hiddenbackupd.conf'

    _local_port = None
    _tor_port = None
    _run_as = None
    _server_password = None
    _cookie_auth = None

    def __init__(self):
        try:
            config = ConfigParser.ConfigParser()
            config.readfp(open(self._config_file))
            self._challenge_port = config.getint('network', '_local_port')
            self._challenge_port = config.getint('network', '_tor_port')
            self._server_password = config.get('tor', 'tor_password')
            self._cookie_auth = config.get('tor', 'cookie_auth')
            self._run_as = config.get('system', 'run_as')
        except ConfigParser.NoOptionError:
            print "Error reading config file."
            exit(2)

    def server_password(self):
        return self._server_password

