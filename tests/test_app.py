import unittest

import os

from checkQC.app import App


class TestApp(unittest.TestCase):

    def setUp(self):
        self.app = App(runfolder=os.path.join(os.path.dirname(__file__), "resources", "MiSeqDemo"))

    def test_run(self):
        # TODO Improve this test once we have better test data
        self.app.run()
        self.assertEqual(self.app.exit_status, 1)


if __name__ == '__main__':
    unittest.main()
