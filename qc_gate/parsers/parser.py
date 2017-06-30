

class Parser(object):

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
