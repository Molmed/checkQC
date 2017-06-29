

class Parser(object):

    def __init__(self):
        self.subscribers = []

    def add_subscribers(self, new_subscribers):
        self.subscribers = self.subscribers + new_subscribers

    def _send_to_subscribers(self, value):
        for subscriber in self.subscribers:
            subscriber.send(value)

    def run(self):
        raise NotImplementedError
