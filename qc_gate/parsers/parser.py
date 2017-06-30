
class Parser(object):
    """
    Parser is the base class for all parser implementations. Please note that it is important that
    all actual implementations are provided as singletons, see e.g. the StatsJsonParser class, since
    all the handlers will attempt to initiate their own parser. However as long as they are singletons
    they should emit each value only once, however if multiple parsers are created you could end up in a
    situation where the same value is emitted a handler multiple times, which might lead to erronous results.
    """

    def __init__(self):
        self.subscribers = []

    def add_subscribers(self, new_subscribers):
        if isinstance(new_subscribers, list):
            self.subscribers = self.subscribers + new_subscribers
        else:
            self.subscribers.append(new_subscribers)

    def _send_to_subscribers(self, value):
        for subscriber in self.subscribers:
            subscriber.send(value)

    def run(self):
        raise NotImplementedError