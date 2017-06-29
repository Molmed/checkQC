

class Parser(object):

    def __init__(self):
        self.subscribers = []

    def add_subscribers(self, new_subscribers):
        self.subscribers = self.subscribers + new_subscribers

    def run(self):
        raise NotImplementedError
