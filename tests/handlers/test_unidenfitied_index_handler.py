import unittest

from collections import Generator

from checkQC.handlers.unidentified_index_handler import UnidentifiedIndexHandler

from tests.test_utils import get_stats_json
from tests.handlers.handler_test_base import HandlerTestBase


class TestUnidentifiedIndexHandler(HandlerTestBase):

    def setUp(self):
        key = "ConversionResults"
        qc_config = {'name': 'UnidentifiedIndexHandler', 'foo': 'aaa'}
        value = get_stats_json()["ConversionResults"]
        undetermined_handler = UnidentifiedIndexHandler(qc_config)
        # TODO
        #undetermined_handler.collect((key, value))
        # TODO Add DemuxSummaryData here!
        self.unidentified_index_handler = undetermined_handler

    def set_qc_config(self, qc_config):
        self.unidentified_index_handler.qc_config = qc_config

    def test_parser_is_list(self):
        self.assertIsInstance(self.unidentified_index_handler.parser(), list)

    def test_check_qc_returns_generator(self):
        self.assertIsInstance(self.unidentified_index_handler.check_qc(), Generator)


    def test_all_is_fine(self):
        # TODO
        pass
#        qc_config = {'name': 'UndeterminedPercentageHandler', 'error': 10, 'warning': 30}
#        self.set_qc_config(qc_config)
#        errors_and_warnings = list(self.unidentified_index_handler.check_qc())
#        self.assertEqual(errors_and_warnings, [])


if __name__ == '__main__':
    unittest.main()
