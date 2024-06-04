import unittest

from checkQC.handlers.q30_handler import Q30Handler

from tests.handlers.handler_test_base import HandlerTestBase


class TestQ30Handler(HandlerTestBase):

    def setUp(self):
        key = "percent_q30"
        qc_config = {"name": "Q30Handler", "error": 70, "warning": 80}
        value_1 = {"lane": 1, "read": 1, "percent_q30": 82}
        value_2 = {"lane": 1, "read": 2, "percent_q30": 50, "is_index_read": True} 
        value_3 = {"lane": 1, "read": 3, "percent_q30": 50, "is_index_read": True} 
        value_4 = {"lane": 1, "read": 4, "percent_q30": 60}
        value_5 = {"lane": 2, "read": 1, "percent_q30": 90}
        value_6 = {"lane": 2, "read": 2, "percent_q30": 50, "is_index_read": True}
        value_7 = {"lane": 2, "read": 3, "percent_q30": 50}
        value_8 = {"lane": 2, "read": 4, "percent_q30": 40}
        q30_handler = Q30Handler(qc_config)
        q30_handler.collect((key, value_1))
        q30_handler.collect((key, value_2))
        q30_handler.collect((key, value_3))
        q30_handler.collect((key, value_4))
        q30_handler.collect((key, value_5))
        q30_handler.collect((key, value_6))
        q30_handler.collect((key, value_7))
        q30_handler.collect((key, value_8))
        self.q30_handler = q30_handler

    def set_qc_config(self, qc_config):
        self.q30_handler.qc_config = qc_config

    def test_all_is_fine(self):
        qc_config = {"name": "Q30Handler", "error": 20, "warning": 30}
        self.set_qc_config(qc_config)
        errors_and_warnings = list(self.q30_handler.check_qc())
        self.assertEqual(errors_and_warnings, [])

    def test_warning(self):
        qc_config = {"name": "Q30Handler", "error": 40, "warning": 60}
        self.set_qc_config(qc_config)
        errors_and_warnings = list(self.q30_handler.check_qc())
        self.assertEqual(len(errors_and_warnings), 5)

        class_names = self.map_errors_and_warnings_to_class_names(errors_and_warnings)
        self.assertListEqual(
            class_names,
            ["QCErrorWarning", "QCErrorWarning", "QCErrorWarning", "QCErrorWarning", "QCErrorWarning"],
        )

    def test_error(self):
        qc_config = {"name": "Q30Handler", "error": 95, "warning": 98}
        self.set_qc_config(qc_config)
        errors_and_warnings = list(self.q30_handler.check_qc())
        self.assertEqual(len(errors_and_warnings), 8)

        self.assertEqual(
            str(errors_and_warnings),
            str("[Fatal QC error: %Q30 82.00 was too low on lane: 1 for read: 1, Fatal QC error: %Q30 50.00 was too low on lane: 1 for index read: 1, Fatal QC error: %Q30 50.00 was too low on lane: 1 for index read: 2, Fatal QC error: %Q30 60.00 was too low on lane: 1 for read: 2, Fatal QC error: %Q30 90.00 was too low on lane: 2 for read: 1, Fatal QC error: %Q30 50.00 was too low on lane: 2 for index read: 1, Fatal QC error: %Q30 50.00 was too low on lane: 2 for read: 2, Fatal QC error: %Q30 40.00 was too low on lane: 2 for read: 3]")
        )

    def test_max_read(self):
        qc_config = {"name": "Q30Handler", "error": 99, "warning": 99}
        self.set_qc_config(qc_config)
        errors_and_warnings = list(self.q30_handler.check_qc())
        self.assertEqual(len(errors_and_warnings), 8)

        [
            self.assertLessEqual(
                int(str(read).split("read: ")[1]), 4
            ) 
            for read in errors_and_warnings
        ]
    


if __name__ == "__main__":
    unittest.main()
