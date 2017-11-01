import unittest

from checkQC.handlers.error_rate_handler import ErrorRateHandler

from tests.handlers.handler_test_base import HandlerTestBase


class TestErrorRateHandler(HandlerTestBase):

    def setUp(self):
        key = "error_rate"
        qc_config = {'name': 'ErrorHandler', 'error': 2, 'warning': 1}
        value_1 = {"lane": 1, "read": 1, "error_rate": 3}
        value_2 = {"lane": 1, "read": 2, "error_rate": 4}
        error_handler = ErrorRateHandler(qc_config)
        error_handler.collect((key, value_1))
        error_handler.collect((key, value_2))
        self.error_handler = error_handler

    def set_qc_config(self, qc_config):
        self.error_handler.qc_config = qc_config

    def test_all_is_fine(self):
        qc_config = {'name': 'ErrorHandler', 'error': 6, 'warning': 5}
        self.set_qc_config(qc_config)
        errors_and_warnings = list(self.error_handler.check_qc())
        self.assertEqual(errors_and_warnings, [])

    def test_warning(self):
        qc_config = {'name': 'ErrorHandler', 'error': 5, 'warning': 3}
        self.set_qc_config(qc_config)
        errors_and_warnings = list(self.error_handler.check_qc())
        self.assertEqual(len(errors_and_warnings), 1)

        class_names = self.map_errors_and_warnings_to_class_names(errors_and_warnings)
        self.assertListEqual(class_names, ['QCErrorWarning'])

    def test_error(self):
        qc_config = {'name': 'ErrorHandler', 'error': 2.9, 'warning': 1}
        self.set_qc_config(qc_config)
        errors_and_warnings = list(self.error_handler.check_qc())
        self.assertEqual(len(errors_and_warnings), 2)

        class_names = self.map_errors_and_warnings_to_class_names(errors_and_warnings)
        self.assertListEqual(class_names, ['QCErrorFatal', 'QCErrorFatal'])

    def test_error_rate_zero_not_allowed(self):
        key = "error_rate"
        value_1 = {"lane": 1, "read": 1, "error_rate": 0}
        value_2 = {"lane": 1, "read": 2, "error_rate": 0}
        # Empty the default list, and then add some more values
        self.error_handler.error_results = []
        self.error_handler.collect((key, value_1))
        self.error_handler.collect((key, value_2))

        qc_config = {'name': 'ErrorHandler', 'error': 2.9, 'warning': 1, 'allow_missing_error_rate': False}
        self.set_qc_config(qc_config)
        errors_and_warnings = list(self.error_handler.check_qc())
        self.assertEqual(len(errors_and_warnings), 2)

        class_names = self.map_errors_and_warnings_to_class_names(errors_and_warnings)
        self.assertListEqual(class_names, ['QCErrorFatal', 'QCErrorFatal'])

    def test_error_rate_zero_is_allowed(self):
        key = "error_rate"
        value_1 = {"lane": 1, "read": 1, "error_rate": 0}
        value_2 = {"lane": 1, "read": 2, "error_rate": 0}
        # Empty the default list, and then add some more values
        self.error_handler.error_results = []
        self.error_handler.collect((key, value_1))
        self.error_handler.collect((key, value_2))

        qc_config = {'name': 'ErrorHandler', 'error': 2.9, 'warning': 1, 'allow_missing_error_rate': True}
        self.set_qc_config(qc_config)
        errors_and_warnings = list(self.error_handler.check_qc())
        self.assertEqual(len(errors_and_warnings), 0)

if __name__ == '__main__':
    unittest.main()
