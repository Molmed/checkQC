import unittest

from checkQC.handlers.undetermined_percentage_handler import UndeterminedPercentageHandler

from tests.test_utils import get_stats_json
from tests.handlers.handler_test_base import HandlerTestBase


class TestUndeterminedPercentageHandler(HandlerTestBase):

    def setUp(self):
        key = "ConversionResults"
        qc_config = {'name': 'UndeterminedPercentageHandler', 'error': 10, 'warning': 20}
        value = get_stats_json()["ConversionResults"]
        undetermined_handler = UndeterminedPercentageHandler(qc_config)
        undetermined_handler.collect((key, value))
        self.undetermined_handler = undetermined_handler

    def set_qc_config(self, qc_config):
        self.undetermined_handler.qc_config = qc_config

    def test_all_is_fine(self):
        qc_config = {'name': 'UndeterminedPercentageHandler', 'error': 10, 'warning': 30}
        self.set_qc_config(qc_config)
        errors_and_warnings = list(self.undetermined_handler.check_qc())
        self.assertEqual(errors_and_warnings, [])

    def test_warning(self):
        qc_config = {'name': 'UndeterminedPercentageHandler', 'error': 4, 'warning': 2}
        self.set_qc_config(qc_config)
        errors_and_warnings = list(self.undetermined_handler.check_qc())
        self.assertEqual(len(errors_and_warnings), 2)

        class_names = self.map_errors_and_warnings_to_class_names(errors_and_warnings)
        self.assertListEqual(class_names, ['QCErrorWarning', 'QCErrorWarning'])

    def test_error(self):
        qc_config = {'name': 'UndeterminedPercentageHandler', 'error': 2, 'warning': 4}
        self.set_qc_config(qc_config)
        errors_and_warnings = list(self.undetermined_handler.check_qc())
        self.assertEqual(len(errors_and_warnings), 2)

        class_names = self.map_errors_and_warnings_to_class_names(errors_and_warnings)
        self.assertListEqual(class_names, ['QCErrorFatal', 'QCErrorFatal'])

if __name__ == '__main__':
    unittest.main()
