import syslog


class Logger:
    def __init__(self):
        syslog.openlog(facility=syslog.LOG_DAEMON)

    def info(self, message):
        syslog.syslog(syslog.LOG_INFO, message)

    def error(self, message):
        syslog.syslog(syslog.LOG_ERR, message)

    def close(self):
        syslog.syslog(syslog.LOG_INFO, 'Closing HSVerifyd')
        syslog.closelog()
