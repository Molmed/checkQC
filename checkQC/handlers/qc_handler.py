

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

    def parser(self):
        raise NotImplementedError("A parser needs to return the class of the parser it needs!")

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

