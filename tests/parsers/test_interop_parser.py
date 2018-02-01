
import os

import unittest

from checkQC.parsers.interop_parser import InteropParser


class TestInteropParser(unittest.TestCase):

    class Receiver(object):
        def __init__(self):
            self.error_rate_values = []
            self.percent_q30_values = []
            self.subscriber = self.subscribe()
            next(self.subscriber)

        def subscribe(self):
            while True:
                interop_stat = yield
                key = list(interop_stat)[0]
                if key == "error_rate":
                    self.error_rate_values.append(interop_stat)
                if key == "percent_q30":
                    self.percent_q30_values.append(interop_stat)

        def send(self, value):
            self.subscriber.send(value)

    runfolder = os.path.join(os.path.dirname(__file__), "..", "resources",
                             "MiSeqDemo")
    interop_parser = InteropParser(runfolder=runfolder, parser_configurations=None)
    subscriber = Receiver()
    interop_parser.add_subscribers(subscriber)
    interop_parser.run()

    def test_read_error_rate(self):
        self.assertListEqual(self.subscriber.error_rate_values,
                             [('error_rate', {'lane': 1, 'read': 1, 'error_rate': 1.5317546129226685}),
                              ('error_rate', {'lane': 1, 'read': 2, 'error_rate': 1.9201501607894897})])


    def test_percent_q30(self):
        self.assertListEqual(self.subscriber.percent_q30_values,
                             [('percent_q30', {'lane': 1, 'read': 1, 'percent_q30': 93.42070007324219}),
                              ('percent_q30', {'lane': 1, 'read': 2, 'percent_q30': 84.4270248413086})])

