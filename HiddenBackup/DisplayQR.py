import json
import subprocess
import sys

from HiddenBackup.ConfigLoader import Config
from HiddenBackup.HiddenService import HiddenService
from HiddenBackup.LogWriter import Logger


class DisplayQR:
    _config = None
    _hs = None
    _log = None

    def __init__(self):
        self._log = Logger()
        self._config = Config()
        self._hs = HiddenService(self._log, self._config.local_port(), self._config.tor_port())

    def display(self):
        # Start hidden services
        if not self._hs.connect(self._config.server_password()):
            print ("Unable to connect to Tor server")
            self._log.close()
            sys.exit(1)

        # Setup paths
        data_dir = self._hs.get_data_dir()
        hostname_path = data_dir + "/hostname"
        clients_path = data_dir + "/client_keys"

        # Read hostname
        try:
            with open(hostname_path, 'r') as hostname:
                host_line = hostname.read()
                host = host_line.split(" ")[0]
                cookie = host_line.split(" ")[1]
        except IOError:
            print("No such file or directory: %s" % hostname_path)
            sys.exit(1)

        # Read cookie
        try:
            with open(clients_path, 'r') as client:
                lines = client.readlines()
                client_name = lines[0].split(" ")[1].replace('\n', '')
        except IOError:
            print("No such file or directory: %s" % clients_path)
            sys.exit(1)

        response = {}
        response["host"] = host
        response["cookie"] = "HidServAuth {0} {1} {2}".format(host, cookie, client_name)
        response["port"] = self._config.tor_port()

        subprocess.call([self._config.qr_bin(), json.dumps(response)])
