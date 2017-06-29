
class Subscriber:

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


class QCErrorFatal(Exception):
    pass


class QCErrorWarning(Exception):
    pass


class QCHandler(Subscriber):

    def __init__(self, pattern, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pattern = pattern
        self.c = 0
        self.exit_status = 0

    def collect(self, value):
        if self.pattern in value:
            self.c += 1
            #print("From subscriber: {}".format(value))

    def check_qc(self):
        if self.c < 11:
            raise QCErrorWarning("C was almost to low...")
        if self.c < 6:
            raise QCErrorFatal("C is way to low, yo!")

    def report(self):
        try:
            self.check_qc()
        except QCErrorWarning as warning:
            print("Warning: {}".format(warning))
        except QCErrorFatal as error:
            print("Error: {}".format(error))

