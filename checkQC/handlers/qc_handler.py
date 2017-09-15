
import logging

log = logging.getLogger()

class Subscriber(object):

    def __init__(self):
        self.subscriber = self.subscribe()
        next(self.subscriber)

    def subscribe(self):
        while True:
            value = yield
            self.collect(value)

    def collect(self):
        raise NotImplementedError()

    def send(self, value):
        self.subscriber.send(value)


class QCErrorFatal(object):
    def __init__(self, msg, ordering=1):
        self.message = msg
        self.ordering = ordering

    def __str__(self):
        return "Fatal QC error: {}".format(self.message)

    def __repr__(self):
        return self.__str__()


class QCErrorWarning(object):
    def __init__(self, msg, ordering=1):
        self.message = msg
        self.ordering = ordering

    def __str__(self):
        return "QC warning: {}".format(self.message)

    def __repr__(self):
        return self.__str__()


class QCHandler(Subscriber):

    UNKNOWN = 'unknown'
    ERROR = 'error'
    WARNING = 'warning'

    def __init__(self, qc_config, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._exit_status = 0
        self.qc_config = qc_config

    def error(self):
        return self.qc_config[self.ERROR]

    def warning(self):
        return self.qc_config[self.WARNING]

    def exit_status(self):
        return self._exit_status

    def parser(self):
        raise NotImplementedError("A parser needs to return the class of the parser it needs!")

    def collect(self, value):
        raise NotImplementedError

    def check_qc(self):
        raise NotImplementedError

    def report(self):
        errors_and_warnings = self.check_qc()
        sorted_errors_and_warnings = sorted(errors_and_warnings, key=lambda x: x.ordering)

        for element in sorted_errors_and_warnings:
            if isinstance(element, QCErrorFatal):
                self._exit_status = 1
                log.error(element)
            else:
                log.warning(element)

