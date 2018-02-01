
import os

import unittest

from checkQC.parsers.stats_json_parser import StatsJsonParser
from checkQC.exceptions import StatsJsonNotFound, ConfigurationError


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
                             "170726_D00118_0303_BCB1TVANXX")
    parser_configs = {"StatsJsonParser": {"bcl2fastq_output_path": "Data/Intensities/BaseCalls"}}
    stats_json_parser = StatsJsonParser(runfolder=runfolder, parser_configurations=parser_configs)
    subscriber = Receiver()
    stats_json_parser.add_subscribers(subscriber)
    stats_json_parser.run()

    def test_read_flowcell_name(self):
        self.assertListEqual(self.subscriber.values, ["CB1TVANXX"])

    def test_init_stats_json_parser_without_valid_parser_config(self):
        with self.assertRaises(ConfigurationError):
            StatsJsonParser("", parser_configurations={"StatsJsonParser": ""})

        with self.assertRaises(ConfigurationError):
            StatsJsonParser("", parser_configurations={"StatsJsonParser": {"invalid_key": "foo"}})

    def test_init_stats_json_parser_without_stats_json(self):
        with self.assertLogs() as cm:
            with self.assertRaises(StatsJsonNotFound):
                StatsJsonParser("", parser_configurations=self.parser_configs)
        expected_log = "ERROR:checkQC.parsers.stats_json_parser:Could not identify a Stats.json file at: " \
                       "Data/Intensities/BaseCalls/Stats/Stats.json. This file is created by bcl2fastq, please ensure that you " \
                       "have run bcl2fastq on this runfolder before running checkqc." \
                       "If this file is not located under <RUNFOLDER>/Data/Intensities/BaseCalls/Stats/Stats.json " \
                       "which is the default option for bcl2fastq, you can specify where the 'Stats' directory is " \
                       "located by changing the 'bcl2fastq_output_path' in the 'StatsJsonParser' part of the " \
                       "checkqc configuration file."
        self.assertIn(expected_log, cm.output)
