from unittest import TestCase

import os

from checkQC.run_type_recognizer import RunTypeRecognizer

class TestRunTypeRecognizer(TestCase):

    CONFIG = {"instrument_type_mappings":{"M": "miseq","D": "hiseq2500","SN": "hiseq2000"}}

    def setUp(self):
        self.runtype_recognizer = RunTypeRecognizer(runfolder=os.path.join(os.path.dirname(__file__),
                                                                           "resources", "Rapid"),
                                                    config=self.CONFIG)

    def test_instrument_type(self):
        expected = "hiseq2500"
        actual = self.runtype_recognizer.instrument_type()
        self.assertEqual(expected, actual.name())

    def test_read_length(self):
        expected = "50"
        actual = self.runtype_recognizer.read_length()
        self.assertEqual(expected, actual)

    def test_run_mode(self):
        expected = "hiseq2500_rapidrun_v2"
        actual = self.runtype_recognizer.instrument_and_reagent_version()
        self.assertEqual(expected, actual)
