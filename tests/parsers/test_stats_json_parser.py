
import os

import unittest

from checkQC.parsers.stats_json_parser import StatsJsonParser


class TestStatsJsonParser(unittest.TestCase):

    class Receiver(object):
        def __init__(self):
            self.values = []
            self.subscriber = self.subscribe()
            next(self.subscriber)

        def subscribe(self):
            while True:
                key, value = yield
                if key == "Flowcell":
                    self.values.append(value)

        def send(self, value):
            self.subscriber.send(value)

    runfolder = os.path.join(os.path.dirname(__file__), "..", "resources",
                             "150418_SN7001335_0149_AH32CYBCXX")
    stats_json_parser = StatsJsonParser(runfolder=runfolder)
    subscriber = Receiver()
    stats_json_parser.add_subscribers(subscriber)
    stats_json_parser.run()

    def test_read_flowcell_name(self):
        self.assertListEqual(self.subscriber.values, ["H32CYBCXX"])

