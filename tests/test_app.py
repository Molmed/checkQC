import unittest

import os

from checkQC.app import App


class TestApp(unittest.TestCase):

    def setUp(self):
        self.app = App(runfolder=os.path.join(os.path.dirname(__file__), "resources", "170726_D00118_0303_BCB1TVANXX/"))

    def test_run(self):
        self.app.run()

    def test_run_json_mode(self):
        app = App(runfolder=os.path.join(os.path.dirname(__file__), "resources", "170726_D00118_0303_BCB1TVANXX/"),
                  json_mode=True)
        app.run()


if __name__ == '__main__':
    unittest.main()
