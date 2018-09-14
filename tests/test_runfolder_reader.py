

from unittest import TestCase

from checkQC.runfolder_reader import RunfolderReader


class TestRunfolderReader(TestCase):

    def test_get_nbr_of_lanes(self):
        actual = RunfolderReader.get_nbr_of_lanes('./tests/resources/170726_D00118_0303_BCB1TVANXX')
        self.assertEqual(actual, 8)
