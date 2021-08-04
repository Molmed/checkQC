import unittest


from tests.test_utils import get_stats_json
from tests.handlers.handler_test_base import HandlerTestBase

from sample_sheet import SampleSheet, Sample

from checkQC.parsers.demux_summary_parser import DemuxSummaryParser
from checkQC.parsers.stats_json_parser import StatsJsonParser
from checkQC.parsers.samplesheet_parser import SamplesheetParser
from checkQC.handlers.unidentified_index_handler import UnidentifiedIndexHandler, _SamplesheetSearcher
from checkQC.exceptions import ConfigurationError
from checkQC.handlers.qc_handler import QCErrorFatal, QCErrorWarning


class TestUnidentifiedIndexHandlerIntegrationTest(HandlerTestBase):

    def setUp(self):
        config = {"StatsJsonParser": {"bcl2fastq_output_path": "Data/Intensities/BaseCalls"},
                  "SamplesheetParser": {"samplesheet_name": "SampleSheet.csv"}}
        runfolder = "./tests/resources/170726_D00118_0303_BCB1TVANXX"
        parsers = [DemuxSummaryParser(runfolder, config),
                   StatsJsonParser(runfolder, config),
                   SamplesheetParser(runfolder, config)]
        qc_config = {
            'name': 'UnidentifiedIndexHandler',
            'significance_threshold': 0.01,
            'white_listed_indexes':
                ['.*N.*', 'G{8,}']
            }
        self.unidentified_index_handler = UnidentifiedIndexHandler(qc_config)
        for parser in parsers:
            parser.add_subscribers(self.unidentified_index_handler)
        for parser in parsers:
            parser.run()

    def test_unidentified_index_handler(self):
        result = self.unidentified_index_handler.check_qc()
        self.assertEqual(len(list(result)), 236)


class TestUnidentifiedIndexHandler(HandlerTestBase):

    def setUp(self):

        qc_config = {
            'name': 'UnidentifiedIndexHandler',
            'significance_threshold': 1,
            'white_listed_indexes':
                ['.*N.*', 'G{8,}']
            }
        self.unidentifiedIndexHandler = UnidentifiedIndexHandler(qc_config)

        conversion_results_key = "ConversionResults"
        conversion_results = get_stats_json()["ConversionResults"]
        samplesheet_key = "samplesheet"
        self.samplesheet = SampleSheet()
        sample_1 = Sample(dict(Lane=1, Sample_ID='1823A', Sample_Name='1823A-tissue', index='AAAA'))
        sample_2 = Sample(dict(Lane=2, Sample_ID='1823B', Sample_Name='1823B-tissue', index='TTTT'))
        sample_3 = Sample(dict(Lane=3, Sample_ID='1823C', Sample_Name='1823C-tissue', index='AAAA', index2='TTTT'))
        sample_4 = Sample(dict(Lane=4, Sample_ID='1823D', Sample_Name='1823D-tissue', index='GGGG', index2='CCCC'))
        sample_5 = Sample(dict(Lane=6, Sample_ID='1823E', Sample_Name='1823D-tissue', index='ATCG'))
        self.samplesheet.add_sample(sample_1)
        self.samplesheet.add_sample(sample_2)
        self.samplesheet.add_sample(sample_3)
        self.samplesheet.add_sample(sample_4)
        self.samplesheet.add_sample(sample_5)

        self.unidentifiedIndexHandler.collect((conversion_results_key, conversion_results))
        self.unidentifiedIndexHandler.collect((samplesheet_key, self.samplesheet))

        self.samplesheet_searcher = _SamplesheetSearcher(self.samplesheet)

    def test_should_be_evaluated(self):
        # No
        self.assertFalse(self.unidentifiedIndexHandler.should_be_evaluated(tag='unknown',
                                                                           count=1,
                                                                           number_of_reads_on_lane=10))
        # No
        self.assertFalse(self.unidentifiedIndexHandler.should_be_evaluated(tag='AAAAAA',
                                                                           count=1,
                                                                           number_of_reads_on_lane=1000))
        # Yes
        self.assertTrue(self.unidentifiedIndexHandler.should_be_evaluated(tag='AAAAAA',
                                                                          count=100,
                                                                          number_of_reads_on_lane=1000))
        # Yes
        self.assertTrue(self.unidentifiedIndexHandler.should_be_evaluated(tag='GGGGGG',
                                                                          count=100,
                                                                          number_of_reads_on_lane=1000))
    
    def test_get_complementary_sequence(self):
        res = self.unidentifiedIndexHandler.get_complementary_sequence('ATCG+N')
        self.assertEqual(res, 'TAGC+N')

    def test_validate_configuration(self):
        with self.assertRaises(ConfigurationError):
            UnidentifiedIndexHandler({'name': 'UnidentifiedIndexHandler', 'foo': 'bar'}).validate_configuration()

    def test_always_warn_rules(self):
        res = next(self.unidentifiedIndexHandler.always_warn_rule(tag="", lane=1, percent_on_lane=1))
        self.assertTrue(isinstance(res, QCErrorFatal))

    def test_always_warn_rules_for_white_listed_tag(self):
        res = next(self.unidentifiedIndexHandler.always_warn_rule(tag="NNNNN", lane=1, percent_on_lane=1))
        self.assertTrue(isinstance(res, QCErrorWarning))

    def test_check_swapped_dual_index_yes(self):
        res = next(self.unidentifiedIndexHandler.check_swapped_dual_index('TTTT+AAAA', 1, self.samplesheet_searcher))
        self.assertTrue('It appears that maybe the dual index tag: TTTT+AAAA was swapped. '
                        'There was a hit for the swapped index: AAAA+TTTT at: Lane: 3, for sample: 1823C-tissue. '
                        'The tag we found in the samplesheet was: AAAA+TTTT' in res.message)

    def test_check_swapped_dual_index_no(self):
        with self.assertRaises(StopIteration):
            next(self.unidentifiedIndexHandler.check_swapped_dual_index('TTGG+AATT', 1, self.samplesheet_searcher))

    def test_check_reversed_index_yes(self):
        res = next(self.unidentifiedIndexHandler.check_reversed_index('GCTA', 1, self.samplesheet_searcher))
        self.assertTrue('We found a possible match for the reverse of tag: GCTA, on: Lane: 6, '
                        'for sample: 1823D-tissue. The tag we found in the samplesheet was: ATCG' in res.message)

    def test_check_reversed_index_no(self):
        with self.assertRaises(StopIteration):
            next(self.unidentifiedIndexHandler.check_reversed_index('GGTT', 1, self.samplesheet_searcher))

    def test_check_complement_index_yes(self):
        res = next(self.unidentifiedIndexHandler.check_complement_index('TTTT', 1, self.samplesheet_searcher))
        self.assertTrue('We found a possible match for the complementary of tag: TTTT, on: Lane: 1, for '
                        'sample: 1823A-tissue. The tag we found in the samplesheet was: AAAA' in res.message)

    def test_check_complement_index_no(self):
        with self.assertRaises(StopIteration):
            next(self.unidentifiedIndexHandler.check_complement_index('GGGG', 1, self.samplesheet_searcher))

    def test_check_if_index_in_other_lane_hit_yes(self):
        res = next(self.unidentifiedIndexHandler.check_if_index_in_other_lane('TTTT', 1, self.samplesheet_searcher))
        self.assertTrue("We found a possible match for the tag: TTTT, on another lane: Lane: 2, for sample: "
                        "1823B-tissue. The tag we found in the samplesheet was: TTTT" in res.message)

    def test_check_if_index_in_other_lane_hit_no(self):
        with self.assertRaises(StopIteration):
            next(self.unidentifiedIndexHandler.check_if_index_in_other_lane('GGGG', 1, self.samplesheet_searcher))

    def test_number_of_reads_per_lane(self):
        res = self.unidentifiedIndexHandler.number_of_reads_per_lane()
        self.assertDictEqual(res, {1: 162726440, 2: 164470667})

    def test_is_significantly_represented(self):
        self.assertTrue(self.unidentifiedIndexHandler.is_significantly_represented(11, 100))
        self.assertFalse(self.unidentifiedIndexHandler.is_significantly_represented(1, 100))

    def test_check_reversed_in_dual_index(self):
        res = next(
            self.unidentifiedIndexHandler.check_reverse_complement_in_dual_index(
                'TTTT+TTTT',
                1,
                self.samplesheet_searcher))
        self.assertTrue('We found a possible match for the reverse complement of tag: TTTT, on: Lane: 1, for sample: '
                        '1823A-tissue. The tag we found in the samplesheet was: AAAA.' in res.message)

    def test_check_reverse_complement_in_dual_index(self):
        res = next(
            self.unidentifiedIndexHandler.check_reverse_complement_in_dual_index(
                'TTTT+TTTT',
                1,
                self.samplesheet_searcher))
        self.assertTrue('We found a possible match for the reverse complement of tag: TTTT, on: Lane: 1,'
                        ' for sample: 1823A-tissue. The tag we found in the samplesheet was: AAAA.' in res.message)

    def test_check_complement_in_dual_index(self):
        res = next(
            self.unidentifiedIndexHandler.check_reverse_complement_in_dual_index(
                'TTTT+TTTT',
                1,
                self.samplesheet_searcher))
        self.assertTrue('We found a possible match for the reverse complement of tag: TTTT, on: Lane: 1, for sample: '
                        '1823A-tissue. The tag we found in the samplesheet was: AAAA.')

if __name__ == '__main__':
    unittest.main()
