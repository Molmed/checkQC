
import logging

from checkQC.config import ConfigurationError

log = logging.getLogger()


class QCHandlerReport(object):
    """
    Base class of objects which contain reports from a QCHandler
    """

    def __init__(self, msg, ordering=1, data=None):
        """
        Instantiate a new QCHandlerReport
        :param msg: Message to send
        :param ordering: A number indicating the ordering of this object in relation to other objects of the same type
                        can be used e.g. to order reports by lane
        :param data: Any additional data (this can e.g. be used to dump additional data into a json object), should be
                     a dict
        """
        self.message = msg
        self.ordering = ordering
        self.data = data

    def type(self):
        """
        Should be implemented by the subclass.
        :return: String with the type of the report, e.g. "error" or "waring"
        """
        raise NotImplementedError("Subclass must implement this method")

    def __repr__(self):
        """
        Providing string representation of this class
        :return: Class string representation
        """
        return self.__str__()

    def as_dict(self):
        """
        Dump the class as a dictionary
        :return: A dict of representing this QCHandlerReport
        """
        return {'type': self.type(), 'message': self.message, 'data': self.data}


class QCErrorFatal(QCHandlerReport):
    def __init__(self, msg, ordering=1, data=None):
        super().__init__(msg, ordering, data)

    def __str__(self):
        return "Fatal QC error: {}".format(self.message)

    def type(self):
        return "error"


class QCErrorWarning(QCHandlerReport):
    def __init__(self, msg, ordering=1, data=None):
        super().__init__(msg, ordering, data)

    def __str__(self):
        return "QC warning: {}".format(self.message)

    def type(self):
        return "warning"


class Subscriber(object):
    """
    Subscriber defined the behaviour necessary to subscribe to data from a Parser. The implementing subclass
    has to implement the `collect` method. This method can decide which objects sent to the Subscriber that
    are of interest to that particular Subscriber, and what should be done with those values.
    """

    def __init__(self):
        self.subscriber = self.subscribe()
        next(self.subscriber)

    def subscribe(self):
        """
        This method picks up data from the parser to which the Subscriber is listening.
        :return:
        """
        while True:
            value = yield
            self.collect(value)

    def collect(self, signal):
        """
        The implementing subclass should provide this method. It is up to instance receiving the data to decide
        how to handle it. Below is an example of how to handle a tuple with a key-value pair.
        ```
        class MySubscriber(Subscriber):

            def __init__(self):
                self.results = []

            def collect(self, signal):
                key, value = signal
                if key == "my_key":
                    self.results.append(value)
        ```
        :return: None
        """
        raise NotImplementedError("Implementing class must provide this method.")

    def send(self, value):
        """
        Will send the specified value to the subscriber
        :param value: Value to send to subscriber
        :return: None
        """
        self.subscriber.send(value)


class QCHandler(Subscriber):

    UNKNOWN = 'unknown'
    ERROR = 'error'
    WARNING = 'warning'

    def __init__(self, qc_config, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._exit_status = 0
        self.qc_config = qc_config

    def custom_configuration_validation(self):
        """
        Override this method in subclass to provide additional configuration behaviour.
        Raise a `ConfigurationError` if there is a problem with the provided config.
        """
        pass

    def validate_configuration(self):
        try:
            self.qc_config[self.ERROR]
            self.qc_config[self.WARNING]
        except KeyError as e:
            raise ConfigurationError("Configuration expects key: {}. Perhaps it is missing?".format(e.args[0]))
        self.custom_configuration_validation()

    def error(self):
        return self.qc_config[self.ERROR]

    def warning(self):
        return self.qc_config[self.WARNING]

    def exit_status(self):
        return self._exit_status

    def parser(self):
        raise NotImplementedError("A handler needs to return the class of the parser it needs!")

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

        return sorted_errors_and_warnings

