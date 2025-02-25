from unittest import TestCase
import mock

import os

from checkQC.exceptions import RunModeUnknown, ReagentVersionUnknown
from checkQC.run_type_recognizer import RunTypeRecognizer, HiSeq2500, MiSeq, NovaSeq, ISeq, NovaSeqXPlus, NextSeq500, NextSeq550
from checkQC.runfolder_reader import RunfolderReader


class TestRunTypeRecognizerFromFolder(TestCase):

    def setUp(self):
        self.runtype_recognizer = RunTypeRecognizer(runfolder=os.path.join(os.path.dirname(__file__),
                                                                           "resources", "Rapid"))

    def test_instrument_type(self):
        expected = "hiseq2500"
        actual = self.runtype_recognizer.instrument_type()
        self.assertEqual(expected, actual.name())

    def test_read_length(self):
        expected = "51"
        actual = self.runtype_recognizer.read_length()
        self.assertEqual(expected, actual)

    def test_run_mode(self):
        expected = "hiseq2500_rapidrun_v2"
        actual = self.runtype_recognizer.instrument_and_reagent_version()
        self.assertEqual(expected, actual)


class TestRunTypeRecognizerCorrectInstrumentsReturned(TestCase):

    def _create_runtype_recognizer(self, instrument_name):
        with mock.patch.object(RunfolderReader, 'read_run_info_xml',
                               return_value={"RunInfo": {"Run": {"Instrument": instrument_name}}}), \
             mock.patch.object(RunfolderReader, 'read_run_parameters_xml', return_value=None):
            return RunTypeRecognizer(runfolder='foo')

    def test_returns_hiseq2500(self):
        runtyperecognizer = self._create_runtype_recognizer("D1000")
        actual = runtyperecognizer.instrument_type()
        self.assertTrue(isinstance(actual, HiSeq2500))

    def test_returns_iseq(self):
        runtyperecognizer = self._create_runtype_recognizer("FS10000263")
        actual = runtyperecognizer.instrument_type()
        self.assertTrue(isinstance(actual, ISeq))

    def test_returns_nextseq550(self):
        runtyperecognizer = self._create_runtype_recognizer("NB551090")
        actual = runtyperecognizer.instrument_type()
        self.assertTrue(isinstance(actual, NextSeq550))

    def test_returns_nextseq500(self):
        runtyperecognizer = self._create_runtype_recognizer("NS500101")
        actual = runtyperecognizer.instrument_type()
        self.assertTrue(isinstance(actual, NextSeq500))

    def test_case_insensitive(self):
        runtyperecognizer = self._create_runtype_recognizer("lh1234")
        actual = runtyperecognizer.instrument_type()
        self.assertTrue(isinstance(actual, NovaSeqXPlus))

        runtyperecognizer = self._create_runtype_recognizer("LH1234")
        actual = runtyperecognizer.instrument_type()
        self.assertTrue(isinstance(actual, NovaSeqXPlus))


class TestIlluminaInstrument(TestCase):

    class MockRunTypeRecognizer():
        def __init__(self, run_parameters):
            self.run_parameters = run_parameters

    def setUp(self):
        self.hiseq2500 = HiSeq2500()
        self.miseq = MiSeq()
        self.novaseq = NovaSeq()
        self.iseq = ISeq()
        self.novaseqxplus = NovaSeqXPlus()
        self.nextseq500 = NextSeq500()
        self.nextseq550 = NextSeq550()

    def test_all_is_well(self):
        runtype_dict = {"RunParameters": {"Setup": {"RunMode": "RapidHighOutput", "Sbs": "HiSeq SBS Kit v4"}}}
        mock_runtype_recognizer = self.MockRunTypeRecognizer(run_parameters=runtype_dict)

        actual = self.hiseq2500.reagent_version(mock_runtype_recognizer)

        expected = "rapidhighoutput_v4"

        self.assertEqual(actual, expected)

    def test_wrong_runmode(self):
        runtype_dict = {"RunParameters": {"Setup": {"Sbs": "HiSeq SBS Kit v4"}}}
        mock_runtype_recognizer = self.MockRunTypeRecognizer(run_parameters=runtype_dict)

        with self.assertRaises(RunModeUnknown):
            self.hiseq2500.reagent_version(mock_runtype_recognizer)

    def test_wrong_reagent(self):
        runtype_dict = {"RunParameters": {"Setup": {"RunMode": "RapidHighOutput"}}}
        mock_runtype_recognizer = self.MockRunTypeRecognizer(run_parameters=runtype_dict)

        with self.assertRaises(ReagentVersionUnknown):
            self.hiseq2500.reagent_version(mock_runtype_recognizer)

    def test_miseq_reagent_version_nano(self):
        runtype_dict = {"RunParameters": {"ReagentKitVersion": "Version2", "Setup": {"NumTilesPerSwath": 2}}}
        mock_runtype_recognizer = self.MockRunTypeRecognizer(run_parameters=runtype_dict)

        actual = self.miseq.reagent_version(mock_runtype_recognizer)

        expected = "nano_v2"

        self.assertEqual(actual, expected)

    def test_miseq_reagent_version_micro(self):
        runtype_dict = {"RunParameters": {"ReagentKitVersion": "Version2", "Setup": {"NumTilesPerSwath": 4}}}
        mock_runtype_recognizer = self.MockRunTypeRecognizer(run_parameters=runtype_dict)

        actual = self.miseq.reagent_version(mock_runtype_recognizer)

        expected = "micro_v2"

        self.assertEqual(actual, expected)

    def test_miseq_reagent_version_standard(self):
        runtype_dict = {"RunParameters": {"ReagentKitVersion": "Version2", "Setup": {"NumTilesPerSwath": 14}}}
        mock_runtype_recognizer = self.MockRunTypeRecognizer(run_parameters=runtype_dict)

        actual = self.miseq.reagent_version(mock_runtype_recognizer)

        expected = "v2"

        self.assertEqual(actual, expected)

    def test_miseq_reagent_version_unrecognized_number_of_tiles(self):
        runtype_dict = {"RunParameters": {"ReagentKitVersion": "Version2", "Setup": {"NumTilesPerSwath": 3}}}
        mock_runtype_recognizer = self.MockRunTypeRecognizer(run_parameters=runtype_dict)

        with self.assertRaises(ReagentVersionUnknown) as cm:
            self.miseq.reagent_version(mock_runtype_recognizer)
            self.assertEqual(cm.exception,
                             "Unable to identify flowcell type through number of tiles per swath")

    def test_miseq_unknown_reagent_version(self):
        runtype_dict = {"RunParameters": {"foo": "bar"}}
        mock_runtype_recognizer = self.MockRunTypeRecognizer(run_parameters=runtype_dict)

        with self.assertRaises(ReagentVersionUnknown):
            self.miseq.reagent_version(mock_runtype_recognizer)

    def test_novaseq_reagent_version_S1(self):
        runtype_dict = {"RunParameters": {"RfidsInfo": {"FlowCellMode": "S1"}}}
        mock_runtype_recognizer = self.MockRunTypeRecognizer(run_parameters=runtype_dict)

        actual = self.novaseq.reagent_version(mock_runtype_recognizer)
        expected = "S1"

        self.assertEqual(actual, expected)

    def test_novaseq_reagent_version_SP(self):
        runtype_dict = {"RunParameters": {"RfidsInfo": {"FlowCellMode": "SP"}}}
        mock_runtype_recognizer = self.MockRunTypeRecognizer(run_parameters=runtype_dict)

        actual = self.novaseq.reagent_version(mock_runtype_recognizer)
        expected = "SP"

        self.assertEqual(actual, expected)

    def test_novaseq_reagent_version_raises(self):
        runtype_dict = {"RunParameters": {"RfidsInfo": {"NoFlowCellMode": "S1"}}}
        mock_runtype_recognizer = self.MockRunTypeRecognizer(run_parameters=runtype_dict)

        with self.assertRaises(ReagentVersionUnknown):
            self.novaseq.reagent_version(mock_runtype_recognizer)

    def test_novaseqxplus_reagent_version(self):
        runtype_dict = {
            "RunParameters": {
                "ConsumableInfo": {
                    "ConsumableInfo": [
                        {"Type": "FlowCell", "Name": "10B"},
                        {"Type": "Reagent"},
                        {"Type": "Buffer"},
                    ]
                }
            }
        }
        mock_runtype_recognizer = self.MockRunTypeRecognizer(run_parameters=runtype_dict)

        actual = self.novaseqxplus.reagent_version(mock_runtype_recognizer)
        expected = "10B"

        self.assertEqual(actual, expected)

    def test_novaseqxplus_reagent_version_old(self):
        runtype_dict = {
            "RunParameters": {
                "ConsumableInfo": {
                    "ConsumableInfo": [
                        {"Type": "FlowCell", "Mode": "10B"},
                        {"Type": "Reagent"},
                        {"Type": "Buffer"},
                    ]
                }
            }
        }
        mock_runtype_recognizer = self.MockRunTypeRecognizer(run_parameters=runtype_dict)

        actual = self.novaseqxplus.reagent_version(mock_runtype_recognizer)
        expected = "10B"

        self.assertEqual(actual, expected)

    def test_novaseqxplus_reagent_version_raises(self):
        runtype_dict = {
            "RunParameters": {
                "ConsumableInfo": {
                    "ConsumableInfo": [
                        {"Type": "FlowCell"},
                        {"Type": "Buffer"},
                    ]
                }
            }
        }
        mock_runtype_recognizer = self.MockRunTypeRecognizer(run_parameters=runtype_dict)

        with self.assertRaises(ReagentVersionUnknown):
            self.novaseqxplus.reagent_version(mock_runtype_recognizer)

    def test_nextseq550_reagent_version_high(self):

        runtype_dict = {
            "RunParameters": {
                "Chemistry": "NextSeq High"
            }
        }

        mock_runtype_recognizer = self.MockRunTypeRecognizer(run_parameters=runtype_dict)
        actual = self.nextseq550.reagent_version(mock_runtype_recognizer)
        expected = "high"

        self.assertEqual(actual, expected)

    def test_nextseq550_reagent_version_mid(self):

        runtype_dict = {
            "RunParameters": {
                "Chemistry": "NextSeq Mid"
            }
        }

        mock_runtype_recognizer = self.MockRunTypeRecognizer(run_parameters=runtype_dict)
        actual = self.nextseq550.reagent_version(mock_runtype_recognizer)
        expected = "mid"

        self.assertEqual(actual, expected)

    def test_nextseq500_reagent_version_high(self):

        runtype_dict = {
            "RunParameters": {
                "Chemistry": "NextSeq High"
            }
        }

        mock_runtype_recognizer = self.MockRunTypeRecognizer(run_parameters=runtype_dict)
        actual = self.nextseq500.reagent_version(mock_runtype_recognizer)
        expected = "high"

        self.assertEqual(actual, expected)

    def test_nextseq500_reagent_version_mid(self):

        runtype_dict = {
            "RunParameters": {
                "Chemistry": "NextSeq Mid"
            }
        }

        mock_runtype_recognizer = self.MockRunTypeRecognizer(run_parameters=runtype_dict)
        actual = self.nextseq500.reagent_version(mock_runtype_recognizer)
        expected = "mid"

        self.assertEqual(actual, expected)
