import os

import stem
from stem.control import Controller


class HiddenService:
    _controller = None
    _log = None
    _local_port = None
    _tor_port = None

    def __init__(self, log, local_port, tor_port):
        self._log = log
        self._local_port = local_port
        self._tor_port = tor_port

    def connect(self, tor_password):
        try:
            self._controller = Controller.from_port()
        except stem.SocketError as exc:
            self._log.error("Unable to connect to tor on port 9051: %s" % exc)
            return False

        try:
            self._controller.authenticate(password=tor_password)
        except stem.connection.MissingPassword:
            self._log.error("Unable to authenticate, missing password")
            return False
        except stem.connection.AuthenticationFailure as exc:
            self._log.error("Unable to authenticate: %s" % exc)
            return False

        return True

    def get_data_dir(self):
        return os.path.join(self._controller.get_conf('DataDirectory', '/tmp'), 'HiddenBackup')

    def bind(self):
        self._controller.create_hidden_service(self.get_data_dir(), self._tor_port, target_port=self._local_port)

    def unbind(self):
        self._controller.remove_hidden_service(self.get_data_dir(), self._local_port)

    def close(self):
        self._controller.close()
