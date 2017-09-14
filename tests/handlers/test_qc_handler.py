
import unittest

from checkQC.handlers.qc_handler import QCHandler, QCErrorWarning, QCErrorFatal


class TestQCHandler(unittest.TestCase):

    expected_qc_errors_and_warning = [QCErrorFatal("1", 1), QCErrorWarning("2", 2),
                                      QCErrorWarning("3", 3), QCErrorFatal("4", 4)]

    random_order_qc_errors_and_warning = [QCErrorWarning("2", 2), QCErrorFatal("1", 1),
                                          QCErrorFatal("4", 4), QCErrorWarning("3", 3)]


    class MockQCHandler(QCHandler):
        # This is a method to mock returning results from the handler
        def check_qc(self):
            return TestQCHandler.random_order_qc_errors_and_warning

    def setUp(self):
        qc_config = {}
        self.qc_handler = self.MockQCHandler(qc_config)

    def test_report_logging_is_ordered(self):
        def fix_names(obj):
            if isinstance(obj, QCErrorFatal):
                return "ERROR:root:{}".format(obj)
            else:
                return "WARNING:root:{}".format(obj)

        expected_logs = list(map(fix_names, TestQCHandler.expected_qc_errors_and_warning))

        with self.assertLogs() as log_checker:
            self.qc_handler.report()

        self.assertEqual(log_checker.output, expected_logs)

if __name__ == '__main__':
    unittest.main()
