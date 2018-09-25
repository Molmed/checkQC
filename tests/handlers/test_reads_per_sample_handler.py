import unittest

from checkQC.handlers.reads_per_sample_handler import ReadsPerSampleHandler

from tests.test_utils import get_stats_json
from tests.handlers.handler_test_base import HandlerTestBase


class TestReadsPerSampleHandler(HandlerTestBase):

    def setUp(self):
        key = "ConversionResults"
        qc_config = {'name': 'ReadsPerSampleHandler', 'error': 'unknown', 'warning': '90'}
        value = get_stats_json()["ConversionResults"]
        reads_per_sample_handler = ReadsPerSampleHandler(qc_config)
        reads_per_sample_handler.collect((key, value))
        self.reads_per_sample_handler = reads_per_sample_handler

    def set_qc_config(self, qc_config):
        self.reads_per_sample_handler.qc_config = qc_config

    def test_all_is_fine(self):
        qc_config = {'name': 'ReadsPerSampleHandler', 'error': '70', 'warning': '90'}
        self.set_qc_config(qc_config)
        errors_and_warnings = list(self.reads_per_sample_handler.check_qc())
        self.assertEqual(errors_and_warnings, [])

    def test_warning(self):
        qc_config = {'name': 'ReadsPerSampleHandler', 'error': '100', 'warning': '400'}
        self.set_qc_config(qc_config)
        errors_and_warnings = list(self.reads_per_sample_handler.check_qc())
        self.assertEqual(len(errors_and_warnings), 4)

        class_names = self.map_errors_and_warnings_to_class_names(errors_and_warnings)
        self.assertListEqual(class_names, ['QCErrorWarning', 'QCErrorWarning',
                                           'QCErrorWarning', 'QCErrorWarning'])

    def test_error(self):
        qc_config = {'name': 'ReadsPerSampleHandler', 'error': '400', 'warning': '500'}
        self.set_qc_config(qc_config)
        errors_and_warnings = list(self.reads_per_sample_handler.check_qc())
        self.assertEqual(len(errors_and_warnings), 4)

        class_names = self.map_errors_and_warnings_to_class_names(errors_and_warnings)
        self.assertListEqual(class_names, ['QCErrorFatal', 'QCErrorFatal',
                                           'QCErrorFatal', 'QCErrorFatal'])

    def test_warning_when_error_unknown(self):
        qc_config = {'name': 'ReadsPerSampleHandler', 'error': 'unknown', 'warning': '400'}
        self.set_qc_config(qc_config)
        errors_and_warnings = list(self.reads_per_sample_handler.check_qc())
        self.assertEqual(len(errors_and_warnings), 4)

        class_names = self.map_errors_and_warnings_to_class_names(errors_and_warnings)
        self.assertListEqual(class_names, ['QCErrorWarning', 'QCErrorWarning',
                                           'QCErrorWarning', 'QCErrorWarning'])

    def test_multiple_sampleIDs_per_sampleName(self):
        key = "ConversionResults"
        qc_config = {'name': 'ReadsPerSampleHandler', 'error': 'unknown', 'warning': '1000'}
        value = get_stats_json("180925_A00001_0001_BABCDEFGXX")["ConversionResults"]
        custom_reads_per_sample_handler = ReadsPerSampleHandler(qc_config)
        custom_reads_per_sample_handler.collect((key, value))
        errors_and_warnings = list(custom_reads_per_sample_handler.check_qc())
        self.assertEqual(len(errors_and_warnings), 4)

        class_names = self.map_errors_and_warnings_to_class_names(errors_and_warnings)
        self.assertListEqual(class_names, ['QCErrorWarning', 'QCErrorWarning',
                                           'QCErrorWarning', 'QCErrorWarning'])

if __name__ == '__main__':
    unittest.main()
