
from pathlib import Path

import unittest

from checkQC.parsers.demux_summary_parser import DemuxSummaryParser
from checkQC.exceptions import ConfigurationError, DemuxSummaryNotFound


class TestDemuxSummaryParser(unittest.TestCase):

    class Receiver(object):
        def __init__(self):
            self.values = []
            self.subscriber = self.subscribe()
            next(self.subscriber)

        def subscribe(self):
            while True:
                res = yield
                self.values.append(res)

        def send(self, value):
            self.subscriber.send(value)

    def setUp(self):
        self.runfolder = Path("tests","resources", "170726_D00118_0303_BCB1TVANXX")
        parser_configs = {"StatsJsonParser": {"bcl2fastq_output_path": "Data/Intensities/BaseCalls"}}
        self.demux_summary_parser = DemuxSummaryParser(runfolder=self.runfolder, parser_configurations=parser_configs)
        self.subscriber = self.Receiver()
        self.demux_summary_parser.add_subscribers(self.subscriber)

    def test_init_stats_summary_demux_without_valid_parser_config(self):
        with self.assertRaises(ConfigurationError):
            DemuxSummaryParser("", parser_configurations={"StatsJsonParser": ""})

        with self.assertRaises(ConfigurationError):
            DemuxSummaryParser("", parser_configurations={"StatsJsonParser": {"invalid_key": "foo"}})

    def test__read_most_popular_unknown_indexes(self):
        actual = self.demux_summary_parser._read_most_popular_unknown_indexes(
            Path(self.runfolder, "Data/Intensities/BaseCalls/Stats/DemuxSummaryF1L1.txt"))
        actual_as_list = list(actual)
        self.assertListEqual(actual_as_list[0:3],
                             [{'count': 41020, 'index': 'CTGAGCTA'},
                              {'count': 31740, 'index': 'NNNNNNNN'},
                              {'count': 28300, 'index': 'GGCTATGA'}])
        self.assertEqual(len(actual_as_list), 1000)

    def test_run(self):
        self.demux_summary_parser.run()
        self.assertEqual(len(self.subscriber.values), 8)
        (first_key, first_value) = self.subscriber.values[0]
        self.assertEqual(first_key, "index_counts")
        self.assertEqual(first_value["lane"], 1)
        self.assertTrue(isinstance(first_value["indices"], list))
        self.assertEqual(len(first_value["indices"]), 1000)
