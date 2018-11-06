
import logging

from checkQC.exceptions import ConfigurationError

log = logging.getLogger(__name__)


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

        :returns: String with the type of the report, e.g. "error" or "warning"
        """
        raise NotImplementedError("Subclass must implement this method")

    def __repr__(self):
        """
        Providing string representation of this class

        :returns: Class string representation
        """
        return self.__str__()

    def as_dict(self):
        """
        Dump the class as a dictionary

        :returns: A dict of representing this QCHandlerReport
        """
        return {'type': self.type(), 'message': self.message, 'data': self.data}


class QCErrorFatal(QCHandlerReport):
    """
    Class representing a fatal QC error from a handler, i.e. a value which should in the end
    yield a non-zero exit status from the program.
    """

    def __init__(self, msg, ordering=1, data=None):
        super().__init__(msg, ordering, data)

    def __str__(self):
        return "Fatal QC error: {}".format(self.message)

    def type(self):
        return "error"


class QCErrorWarning(QCHandlerReport):
    """
    Class representing a QC warning from a handler, i.e. a value is interesting to note,
    but which should still yield a zero exit status from the program.
    """
    def __init__(self, msg, ordering=1, data=None):
        super().__init__(msg, ordering, data)

    def __str__(self):
        return "QC warning: {}".format(self.message)

    def type(self):
        return "warning"


class Subscriber(object):
    """
    Subscriber defines the behaviour necessary to subscribe to data from a Parser. The implementing subclass
    has to implement the `collect` method. This method can decide which objects sent to the Subscriber that
    are of interest to that particular Subscriber, and what should be done with those values.
    """

    def __init__(self):
        self.subscriber = self.subscribe()
        next(self.subscriber)

    def subscribe(self):
        """
        This method picks up data from the parser to which the Subscriber is listening.

        :returns: None
        """
        while True:
            value = yield
            self.collect(value)

    def collect(self, signal):
        """
        The implementing subclass should provide this method. It is up to instance receiving the data to decide
        how to handle it. Below is an example of how to handle a tuple with a key-value pair.

        .. code-block :: python

            class MySubscriber(Subscriber):

                def __init__(self):
                    self.results = []

                def collect(self, signal):
                    key, value = signal
                    if key == "my_key":
                        self.results.append(value)


        :returns: None
        """
        raise NotImplementedError("Implementing class must provide this method.")

    def send(self, value):
        """
        Will send the specified value to the subscriber

        :param value: Value to send to subscriber
        :returns: None
        """
        self.subscriber.send(value)


class QCHandler(Subscriber):
    """
    The QCHandler is one of the fundamental classes of CheckQC. It is the base class for the the concrete
    implementations of QCHandlers which actually check the the quality criteria of a runfolder.
    For examples of how to implement a QCHandler it is easiest to look at the implementations available in
    the `checkQC.handlers` module
    """

    UNKNOWN = 'unknown'
    ERROR = 'error'
    WARNING = 'warning'

    def __init__(self, qc_config):
        """
        Create a QCHandler instance

        :param qc_config: dict containing the configuration for the QCHandler. Should have keys 'error' and 'warning'
        """
        super().__init__()
        self._exit_status = 0
        self.qc_config = qc_config

    def custom_configuration_validation(self):
        """
        Override this method in subclass to provide additional configuration behaviour.

        :raises: ConfigurationError if there is a problem with the configuration
        """
        pass

    def validate_configuration(self):
        """
        This method will validate the configuration which has been passed to the QCHandler. This should be called
        by the class making use of this instance. It will not be called automatically e.g. at object creation.

        :returns: None
        :raises: ConfigurationError if there is a problem with the configuration
        """
        try:
            self.qc_config[self.ERROR]
            self.qc_config[self.WARNING]
        except KeyError as e:
            raise ConfigurationError("Configuration expects key: {}. Perhaps it is missing?".format(e.args[0]))
        self.custom_configuration_validation()

    def error(self):
        """
        The value associated with a QC error

        :returns: The configuration value for an error
        """
        return self.qc_config[self.ERROR]

    def warning(self):
        """
        The value associated with a QC warning

        :returns: The configuration value for an warning
        """
        return self.qc_config[self.WARNING]

    def exit_status(self):
        """
        The exit status of the handler.

        :returns: 0 if the qc criteria have not encountered a fatal qc error, else 1.
        """
        return self._exit_status

    def parser(self):
        """
        The class of the Parser (or a list of parsers) which this QCHandler will get its data from.
        E.g.

        .. code-block :: python

            def parser(self):
                return InteropParser

        Note that there should be no parenthesis after the class.

        :returns: The Parser implementation needed by this QCHandler
        """
        raise NotImplementedError("A handler needs to return the class of the parser it needs!")

    def check_qc(self):
        """
        The check_qc method provides the core behaviour of the QCHandler. It should check the values provided
        to it and yield instances of QCHandlerReport (or continue, if there was nothing to report)

        :returns: An instance of QCHandlerReport
        """
        raise NotImplementedError("A handler must provide its own QC checking behaviour by implementing "
                                  "the `check_qc` method.")

    def report(self):
        """
        Check the quality criteria as specified in `check_qc` and gather all reports. Will set the objects
        `exit_status` in accordance with what types of reports are found.

        :returns: A sorted list of errors and warnings found when evaluating the qc criteria.
        """
        errors_and_warnings = self.check_qc()
        sorted_errors_and_warnings = sorted(errors_and_warnings, key=lambda x: x.ordering)

        for element in sorted_errors_and_warnings:
            if isinstance(element, QCErrorFatal):
                self._exit_status = 1
                log.error(element)
            else:
                log.warning(element)

        return sorted_errors_and_warnings

