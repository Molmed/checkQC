import unittest

import os

from checkQC.app import App


class TestApp(unittest.TestCase):

    RUNFOLDER = os.path.join(os.path.dirname(__file__), "resources", "170726_D00118_0303_BCB1TVANXX/")

    def test_run(self):
        app = App(runfolder=self.RUNFOLDER)
        # The test data contains fatal qc errors
        self.assertEqual(app.run(), 1)

    def test_run_json_mode(self):
        app = App(runfolder=self.RUNFOLDER, json_mode=True)
        # The test data contains fatal qc errors
        self.assertEqual(app.run(), 1)

    def test_run_use_closest_read_length(self):
        config_file = os.path.join("tests", "resources", "read_length_not_in_config.yaml")
        app = App(runfolder=self.RUNFOLDER, config_file=config_file, use_closest_read_length=True)
        # The test data contains fatal qc errors
        self.assertEqual(app.run(), 1)

    def test_run_downgrade_error(self):
        app = App(runfolder=self.RUNFOLDER, downgrade_errors_for="ReadsPerSampleHandler")
        # Test data should not produce fatal qc errors anymore
        self.assertEqual(app.run(), 0)

if __name__ == '__main__':
    unittest.main()
