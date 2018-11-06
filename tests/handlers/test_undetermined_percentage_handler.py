import unittest

from checkQC.handlers.undetermined_percentage_handler import UndeterminedPercentageHandler

from tests.test_utils import get_stats_json
from tests.handlers.handler_test_base import HandlerTestBase


class TestUndeterminedPercentageHandler(HandlerTestBase):

    def setUp(self):
        conversion_key = "ConversionResults"
        qc_config = {'name': 'UndeterminedPercentageHandler', 'error': 10, 'warning': 20}
        conversion_results_value = get_stats_json()["ConversionResults"]
        undetermined_handler = UndeterminedPercentageHandler(qc_config)
        undetermined_handler.collect((conversion_key, conversion_results_value))

        percentage_phix_key = "percent_phix"
        percentage_phix_value_lane_1_read_1 = {"lane": 1, "read": 1, "percent_phix": 1}
        percentage_phix_value_lane_1_read_2 = {"lane": 1, "read": 2, "percent_phix": 1}
        percentage_phix_value_lane_2_read_1 = {"lane": 2, "read": 1, "percent_phix": 1}
        percentage_phix_value_lane_2_read_2 = {"lane": 2, "read": 2, "percent_phix": 1}
        undetermined_handler.collect((percentage_phix_key, percentage_phix_value_lane_1_read_1))
        undetermined_handler.collect((percentage_phix_key, percentage_phix_value_lane_1_read_2))
        undetermined_handler.collect((percentage_phix_key, percentage_phix_value_lane_2_read_1))
        undetermined_handler.collect((percentage_phix_key, percentage_phix_value_lane_2_read_2))

        self.undetermined_handler = undetermined_handler

    def set_qc_config(self, qc_config):
        self.undetermined_handler.qc_config = qc_config

    def test_all_is_fine(self):
        qc_config = {'name': 'UndeterminedPercentageHandler', 'error': 10, 'warning': 30}
        self.set_qc_config(qc_config)
        errors_and_warnings = list(self.undetermined_handler.check_qc())
        self.assertEqual(errors_and_warnings, [])

    def test_warning(self):
        qc_config = {'name': 'UndeterminedPercentageHandler', 'error': 2, 'warning': 1}
        self.set_qc_config(qc_config)
        errors_and_warnings = list(self.undetermined_handler.check_qc())
        self.assertEqual(len(errors_and_warnings), 2)

        class_names = self.map_errors_and_warnings_to_class_names(errors_and_warnings)
        self.assertListEqual(class_names, ['QCErrorWarning', 'QCErrorWarning'])

    def test_error(self):
        qc_config = {'name': 'UndeterminedPercentageHandler', 'error': 1, 'warning': 0}
        self.set_qc_config(qc_config)
        errors_and_warnings = list(self.undetermined_handler.check_qc())
        self.assertEqual(len(errors_and_warnings), 2)

        class_names = self.map_errors_and_warnings_to_class_names(errors_and_warnings)
        self.assertListEqual(class_names, ['QCErrorFatal', 'QCErrorFatal'])

    def test_no_yield(self):
        key = "ConversionResults"
        value = get_stats_json()["ConversionResults"]
        value[0]["Yield"] = 0
        self.undetermined_handler.collect((key, value))

        errors_and_warnings = list(self.undetermined_handler.check_qc())
        class_names = self.map_errors_and_warnings_to_class_names(errors_and_warnings)
        self.assertListEqual(class_names, ['QCErrorFatal'])


if __name__ == '__main__':
    unittest.main()
