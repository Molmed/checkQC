import unittest

import os

from checkQC.app import App


class TestApp(unittest.TestCase):

    def setUp(self):
        self.app = App(runfolder=os.path.join(os.path.dirname(__file__), "resources", "MiSeqDemo"))

    def test_run_with_non_existent_file(self):
        # TODO Improve this test once we have better test data
        with self.assertRaises(FileNotFoundError):
            self.app.run()


if __name__ == '__main__':
    unittest.main()
