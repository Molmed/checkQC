
import importlib
import pkgutil


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
    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return "Fatal error: {}".format(self.message)

    def __repr__(self):
        return self.__str__()


class QCErrorWarning(object):
    def __init__(self, msg):
        self.message = msg

    def __str__(self):
        return "Warning: {}".format(self.message)

    def __repr__(self):
        return self.__str__()


class QCHandlerNotFoundException(Exception):
    pass


class QCHandler(Subscriber):

    handlers = []
    parsers = set()
    runfolder = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.exit_status = 0

    def initiate_parser(self, runfolder):
        parser = self.parser(runfolder)
        parser.add_subscribers(self)
        return parser

    def parser(self, runfolder):
        raise NotImplementedError

    def collect(self, value):
        raise NotImplementedError

    def check_qc(self):
        raise NotImplementedError

    def report(self):
        errors_and_warnings = self.check_qc()

        for element in errors_and_warnings:
            if isinstance(element, QCErrorFatal):
                self.exit_status = 1
            print(element)

    @staticmethod
    def create_subclass_instance(class_name, class_config):
        """
        This method will look for a class with the given `class_name` in the `qc_gate.handlers` module.
        If it can find a class with a matching name it will return a instance of that class.
        :param class_name: the name of the class to instantiate
        :param class_config: dictionary with configuration for the class
        :return: A instance of the class represented by class_name
        """
        pkgs = list(pkgutil.walk_packages('checkQC.handlers'))
        for importer, modname, ispkg in pkgs:
            if "checkQC.handlers" in modname:
                importlib.import_module(modname)
        qc_handler_subclasses = list(QCHandler.__subclasses__())
        try:
            i = list(map(lambda clazz: clazz.__name__, qc_handler_subclasses)).index(class_name)
            return qc_handler_subclasses[i](class_config)
        except ValueError:
            raise QCHandlerNotFoundException("Could not identify a QCHandler with name: {}".format(class_name))

