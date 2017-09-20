import unittest

from checkQC.handlers.yield_handler import YieldHandler

from tests.test_utils import get_stats_json
from tests.handlers.handler_test_base import HandlerTestBase


class TestYieldHandler(HandlerTestBase):

    def setUp(self):
        key = "ConversionResults"
        qc_config = {'name': 'YieldHandler', 'error': 10, 'warning': 20}
        value = get_stats_json()["ConversionResults"]
        yield_handler = YieldHandler(qc_config)
        yield_handler.collect((key, value))
        self.yield_handler = yield_handler

    def set_qc_config(self, qc_config):
        self.yield_handler.qc_config = qc_config

    def test_all_is_fine(self):
        qc_config = {'name': 'YieldHandler', 'error': 10, 'warning': 20}
        self.set_qc_config(qc_config)
        errors_and_warnings = list(self.yield_handler.check_qc())
        self.assertEqual(errors_and_warnings, [])

    def test_warning(self):
        qc_config = {'name': 'YieldHandler', 'error': 10, 'warning': 40}
        self.set_qc_config(qc_config)
        errors_and_warnings = list(self.yield_handler.check_qc())
        self.assertEqual(len(errors_and_warnings), 2)

        class_names = self.map_errors_and_warnings_to_class_names(errors_and_warnings)
        self.assertListEqual(class_names, ['QCErrorWarning', 'QCErrorWarning'])

    def test_error(self):
        qc_config = {'name': 'YieldHandler', 'error': 40, 'warning': 50}
        self.set_qc_config(qc_config)
        errors_and_warnings = list(self.yield_handler.check_qc())
        self.assertEqual(len(errors_and_warnings), 2)

        class_names = self.map_errors_and_warnings_to_class_names(errors_and_warnings)
        self.assertListEqual(class_names, ['QCErrorFatal', 'QCErrorFatal'])

if __name__ == '__main__':
    unittest.main()
