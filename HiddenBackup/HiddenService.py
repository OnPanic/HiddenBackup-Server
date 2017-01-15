import os

import stem
from stem.control import Controller


class HiddenService:
    _controller = None
    _log = None

    def __init__(self, log):
        self._log = log

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

    def remove_bind(self, hidden_services):
        for service in hidden_services:
            self._controller.remove_hidden_service(self.get_data_dir(), service[1])

    def remove_own(self):
        self._controller.remove_hidden_service(self.get_data_dir(), 8888)

    def set_own(self, challenge_port):
        self._controller.create_hidden_service(self.get_data_dir(), 8888, target_port=challenge_port)

    def bind(self, hidden_services):
        for service in hidden_services:
            self._controller.create_hidden_service(self.get_data_dir(), service[1], target_port=service[0])

    def close(self):
        self._controller.close()
