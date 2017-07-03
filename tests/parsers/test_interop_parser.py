
import unittest

from checkQC.parsers.interop_parser import InteropParser


class TestInteropParser(unittest.TestCase):

    class Receiver(object):
        def __init__(self):
            self.values = []
            self.subscriber = self.subscribe()
            next(self.subscriber)

        def subscribe(self):
            while True:
                value = yield
                self.values.append(value)

        def send(self, value):
            self.subscriber.send(value)

    interop_parser = InteropParser(runfolder="MiSeqDemo")
    subscriber = Receiver()
    interop_parser.add_subscribers(subscriber)
    interop_parser.run()

    def test_read_error_rate(self):
        self.assertListEqual(self.subscriber.values,
                             [{'error_rate': {'lane': 1, 'read': 1, 'error_rate': 1.5317546129226685}},
                              {'error_rate': {'lane': 1, 'read': 2, 'error_rate': 1.9201501607894897}}])
