from pathlib import Path

import tornado.web
from tornado.testing import *
import json

from checkQC.web_app import WebApp
from checkQC import __version__


class TestWebApp(AsyncHTTPTestCase):

    def get_app(self):
        routes = WebApp._routes(
            monitoring_path="tests/resources/monitored_dir",
            qc_config_file=None
        )
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
        routes = WebApp._routes(
            monitoring_path="tests/resources/monitored_dir",
            qc_config_file="tests/resources/incomplete_config.yaml"
        )
        return tornado.web.Application(routes)

    def test_qc_fail_fast_for_unknown_config(self):
        response = self.fetch('/qc/170726_D00118_0303_BCB1TVANXX')
        self.assertEqual(response.code, 500)


class TestWebAppReadLengthNotInConfig(AsyncHTTPTestCase):

    def get_app(self):
        routes = WebApp._routes(
            monitoring_path="tests/resources/monitored_dir",
            qc_config_file="tests/resources/read_length_not_in_config.yaml",
        )
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
        expected_keys = [
            'qc_reports' ,
            'version',
            'exit_status'
        ]

        response = self.fetch(
            "/qc/200624_A00834_0183_BHMTFYTINY"
            "?demultiplexer=bclconvert"
            "&useClosestReadLength"
        )
        self.assertEqual(response.code, 200)
        result = json.loads(response.body)
        self.assertEqual(result["exit_status"], 1)
        self.assertEqual(result["version"], __version__)
        self.assertEqual(list(result.keys()), expected_keys)
