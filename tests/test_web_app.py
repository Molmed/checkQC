

import tornado.web
from tornado.testing import *

from checkQC.web_app import WebApp


class TestWebApp(AsyncHTTPTestCase):

    def get_app(self):
        routes = WebApp._routes(monitoring_path=os.path.join("tests", "resources"), qc_config_file=None)
        return tornado.web.Application(routes)

    def test_qc_endpoint(self):
        response = self.fetch('/qc/170726_D00118_0303_BCB1TVANXX')
        self.assertEqual(response.code, 200)

    def test_qc_invalid_endpoint(self):
        response = self.fetch('/qc/foo')
        self.assertEqual(response.code, 404)


class TestWebAppWithNonUsefulConfig(AsyncHTTPTestCase):

    def get_app(self):
        routes = WebApp._routes(monitoring_path=os.path.join("tests", "resources"),
                                qc_config_file=os.path.join("tests", "resources", "incomplete_config.yaml"))
        return tornado.web.Application(routes)

    def test_qc_fail_fast_for_unknown_config(self):
        response = self.fetch('/qc/170726_D00118_0303_BCB1TVANXX')
        self.assertEqual(response.code, 500)
