import unittest

from checkQC.handlers.q30_handler import Q30Handler

from tests.handlers.handler_test_base import HandlerTestBase


class TestQ30Handler(HandlerTestBase):

    def setUp(self):
        key = "percent_q30"
        qc_config = {'name': 'Q30Handler', 'error': 70, 'warning': 80}
        value_1 = {"lane": 1, "read": 1, "percent_q30": 82}
        value_2 = {"lane": 1, "read": 2, "percent_q30": 90}
        q30_handler = Q30Handler(qc_config)
        q30_handler.collect((key, value_1))
        q30_handler.collect((key, value_2))
        self.q30_handler = q30_handler

    def set_qc_config(self, qc_config):
        self.q30_handler.qc_config = qc_config

    def test_all_is_fine(self):
        qc_config = {'name': 'Q30Handler', 'error': 70, 'warning': 80}
        self.set_qc_config(qc_config)
        errors_and_warnings = list(self.q30_handler.check_qc())
        self.assertEqual(errors_and_warnings, [])

    def test_warning(self):
        qc_config = {'name': 'Q30Handler', 'error': 70, 'warning': 85}
        self.set_qc_config(qc_config)
        errors_and_warnings = list(self.q30_handler.check_qc())
        self.assertEqual(len(errors_and_warnings), 1)

        class_names = self.map_errors_and_warnings_to_class_names(errors_and_warnings)
        self.assertListEqual(class_names, ['QCErrorWarning'])

    def test_error(self):
        qc_config = {'name': 'Q30Handler', 'error': 95, 'warning': 98}
        self.set_qc_config(qc_config)
        errors_and_warnings = list(self.q30_handler.check_qc())
        self.assertEqual(len(errors_and_warnings), 2)

        class_names = self.map_errors_and_warnings_to_class_names(errors_and_warnings)
        self.assertListEqual(class_names, ['QCErrorFatal', 'QCErrorFatal'])

if __name__ == '__main__':
    unittest.main()
