
from concurrent.futures import ProcessPoolExecutor

import tornado.web
from tornado.testing import *

from checkQC.web_app import WebApp, CheckQCHandler


class TestWebApp(AsyncHTTPTestCase):

    def get_app(self):
        routes = WebApp._routes(monitoring_path=os.path.join("tests", "resources"),
                                qc_config_file=None)
        CheckQCHandler.process_pool = ProcessPoolExecutor()
        return tornado.web.Application(routes)


    def test_qc_endpoint(self):
        response = self.fetch('/qc/170726_D00118_0303_BCB1TVANXX')
        self.assertEqual(response.code, 200)

