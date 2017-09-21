import unittest

from checkQC.handlers.cluster_pf_handler import ClusterPFHandler

from tests.test_utils import get_stats_json
from tests.handlers.handler_test_base import HandlerTestBase


class TestClusterPFHandler(HandlerTestBase):

    def setUp(self):
        key = "ConversionResults"
        qc_config = {'name': 'TotalClustersPF', 'error': '50', 'warning': '110'}
        value = get_stats_json()["ConversionResults"]
        cluster_pf_handler = ClusterPFHandler(qc_config)
        cluster_pf_handler.collect((key, value))
        self.cluster_pf_handler = cluster_pf_handler

    def set_qc_config(self, qc_config):
        self.cluster_pf_handler.qc_config = qc_config

    def test_all_is_fine(self):
        qc_config = {'name': 'TotalClustersPF', 'error': 'unknown', 'warning': '110'}
        self.set_qc_config(qc_config)
        errors_and_warnings = list(self.cluster_pf_handler.check_qc())
        self.assertEqual(errors_and_warnings, [])

    def test_warning(self):
        qc_config = {'name': 'TotalClustersPF', 'error': '100', 'warning': '170'}
        self.set_qc_config(qc_config)
        errors_and_warnings = list(self.cluster_pf_handler.check_qc())
        self.assertEqual(len(errors_and_warnings), 2)

        class_names = self.map_errors_and_warnings_to_class_names(errors_and_warnings)
        self.assertListEqual(class_names, ['QCErrorWarning', 'QCErrorWarning'])

    def test_error(self):
        qc_config = {'name': 'TotalClustersPF', 'error': '170', 'warning': '180'}
        self.set_qc_config(qc_config)
        errors_and_warnings = list(self.cluster_pf_handler.check_qc())
        self.assertEqual(len(errors_and_warnings), 2)

        class_names = self.map_errors_and_warnings_to_class_names(errors_and_warnings)
        self.assertListEqual(class_names, ['QCErrorFatal', 'QCErrorFatal'])

    def test_warning_when_error_unknown(self):
        qc_config = {'name': 'TotalClustersPF', 'error': 'unknown', 'warning': '170'}
        self.set_qc_config(qc_config)
        errors_and_warnings = list(self.cluster_pf_handler.check_qc())
        self.assertEqual(len(errors_and_warnings), 2)

        class_names = self.map_errors_and_warnings_to_class_names(errors_and_warnings)
        self.assertListEqual(class_names, ['QCErrorWarning', 'QCErrorWarning'])


if __name__ == '__main__':
    unittest.main()
