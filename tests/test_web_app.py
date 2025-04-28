

import tornado.web
from tornado.testing import *
import json

from checkQC.web_app import WebApp


class TestWebApp(AsyncHTTPTestCase):

    def get_app(self):
        routes = WebApp._routes(monitoring_path=os.path.join("tests", "resources"), qc_config_file=None)
        return tornado.web.Application(routes)

    def test_qc_endpoint(self):
        response = self.fetch('/qc/170726_D00118_0303_BCB1TVANXX')
        self.assertEqual(response.code, 200)
        result = json.loads(response.body)
        # Test data produce fatal qc errors
        self.assertEqual(result["exit_status"], 1)

    def test_qc_invalid_endpoint(self):
        response = self.fetch('/qc/foo')
        self.assertEqual(response.code, 404)

    def test_qc_downgrade_errors(self):
        response = self.fetch('/qc/170726_D00118_0303_BCB1TVANXX?downgrade=ReadsPerSampleHandler,UndeterminedPercentageHandler')
        result = json.loads(response.body)
        self.assertEqual(response.code, 200)
        # Test data no longer produce fatal qc errors
        self.assertEqual(result["exit_status"], 0)


class TestWebAppWithNonUsefulConfig(AsyncHTTPTestCase):

    def get_app(self):
        routes = WebApp._routes(monitoring_path=os.path.join("tests", "resources"),
                                qc_config_file=os.path.join("tests", "resources", "incomplete_config.yaml"))
        return tornado.web.Application(routes)

    def test_qc_fail_fast_for_unknown_config(self):
        response = self.fetch('/qc/170726_D00118_0303_BCB1TVANXX')
        self.assertEqual(response.code, 500)


class TestWebAppReadLengthNotInConfig(AsyncHTTPTestCase):

    def get_app(self):
        routes = WebApp._routes(monitoring_path=os.path.join("tests", "resources"),
                                qc_config_file=os.path.join("tests", "resources", "read_length_not_in_config.yaml"))
        return tornado.web.Application(routes)

    def test_use_closest_read_length(self):
        response = self.fetch('/qc/170726_D00118_0303_BCB1TVANXX?useClosestReadLength')
        result = json.loads(response.body)
        self.assertEqual(response.code, 200)
        # Test data produce fatal qc errors
        self.assertEqual(result["exit_status"], 1)

    def test_use_closest_read_length_and_downgrade_errors(self):
        response = self.fetch('/qc/170726_D00118_0303_BCB1TVANXX?useClosestReadLength&downgrade=ReadsPerSampleHandler')
        result = json.loads(response.body)
        self.assertEqual(response.code, 200)
        # Test data produce fatal qc errors
        self.assertEqual(result["exit_status"], 0)

    def test_qc_endpoint_bclconvert(self):
        expected_data = {
            'lane reports': {
                '1': {
                    'error_rate': [
                        'Fatal QC error: Error rate is nan on lane 1 for read 1. '
                        'This may be because no PhiX was loaded on this lane. '
                        'Use "allow_missing_error_rate: true" to disable this error message.'
                    ],
                    'reads_per_sample': [
                        'Fatal QC error: Number of reads for sample '
                        'Sample_14574-Qiagen-IndexSet1-SP-Lane1 on lane 1 were too low: '
                        '0.00992 M (threshold: 0.5 M)',
                        'Fatal QC error: Number of reads for sample '
                        'Sample_14575-Qiagen-IndexSet1-SP-Lane1 on lane 1 were too low: '
                        '0.00856 M (threshold: 0.5 M)',
                    ],
                    'undetermined_percentage': [
                        'Fatal QC error: Percentage of undetermined indices '
                        '99.46% (- 0.00% phiX) > 9.00% on lane 1.'
                    ]
                },
                '2': {
                    'error_rate': [
                        'Fatal QC error: Error rate is nan on lane 2 for read 1. '
                        'This may be because no PhiX was loaded on this lane. '
                        'Use "allow_missing_error_rate: true" to disable this error message.'
                    ],
                    'reads_per_sample': [
                        'Fatal QC error: Number of reads for sample '
                        'Sample_14574-Qiagen-IndexSet1-SP-Lane2 on lane 2 were too low: '
                        '0.010208 M (threshold: 0.5 M)',
                        'Fatal QC error: Number of reads for sample '
                        'Sample_14575-Qiagen-IndexSet1-SP-Lane2 on lane 2 were too low: '
                        '0.008672 M (threshold: 0.5 M)',
                    ],
                    'undetermined_percentage': [
                        'Fatal QC error: Percentage of undetermined indices '
                        '99.45% (- 0.00% phiX) > 9.00% on lane 2.'
                    ]
                }
            },
            'run_summary': {
                'instrument_and_reagent_version': 'novaseq_SP',
                'read_length': 36,
                'checkers': {
                    'UndeterminedPercentageHandler': {
                        'warning_threshold': 'unknown', 'error_threshold': 9
                    },
                    'UnidentifiedIndexHandler': {
                        'significance_threshold': 1,
                        'white_listed_indexes': ['.*N.*', 'G{6,}']
                    },
                    'ClusterPFHandler': {
                        'warning_threshold': 1, 'error_threshold': 'unknown'
                    },
                    'Q30Handler': {
                        'warning_threshold': 1, 'error_threshold': 'unknown'
                    },
                    'ErrorRateHandler': {
                        'allow_missing_error_rate': False,
                        'warning_threshold': 2, 'error_threshold': 'unknown'
                    },
                    'ReadsPerSampleHandler': {
                        'warning_threshold': 'unknown', 'error_threshold': 1
                    }
                }
            },
            'version': '4.0.6',
            'exit_status': 1
        }

        response = self.fetch(
            "/qc/200624_A00834_0183_BHMTFYTINY"
            "?demultiplexer=bclconvert"
            "&useClosestReadLength"
        )
        self.assertEqual(response.code, 200)
        result = json.loads(response.body)
        self.assertEqual(result["exit_status"], 1)
        self.assertEqual(result, expected_data)

