
import logging

from checkQC.exceptions import *
from checkQC.runfolder_reader import RunfolderReader

log = logging.getLogger(__name__)


class IlluminaInstrument(object):
    """
    Base class representing an Illumina instrument. The `name` and `reagent_version` needs to be implemented
    by the specific subclasses.
    """

    @staticmethod
    def get_subclasses():
        """
        Get all subclasses which extends this class (which should be all supported Illumina instruments)

        :returns: a list of IlluminaInstrument subclasses
        """
        return IlluminaInstrument.__subclasses__()

    @staticmethod
    def create_instrument_instance(instrument_name):
        """
        Get the instrument instance corresponding to the given instrument name

        :param instrument_name: name of instrument to get the implementing class for
        :returns: a instance of the corresponding IlluminaInstrument
        """
        subclasses = IlluminaInstrument.get_subclasses()
        for subclass in subclasses:
            if instrument_name == subclass.name():
                return subclass()
        raise InstrumentTypeUnknown

    @staticmethod
    def name():
        """
        Name of the instrument, e.g. 'nova_seq'

        :returns: name of instrument as string
        """
        raise NotImplementedError

    @staticmethod
    def reagent_version(runtype_recognizer):
        """
        Reagent version, e.g. `v1`
        Can used the provided runtype_recognizer to determined the exact reagent version

        :param runtype_recognizer: A instance of RuntypeRecognizer
        :returns: reagent version as a string
        """
        raise NotImplementedError

class ISeq(IlluminaInstrument):

    @staticmethod
    def name():
        return "iseq"

    @staticmethod
    def reagent_version(runtype_recognizer):
        return "v1"

class NovaSeq(IlluminaInstrument):

    @staticmethod
    def name():
        return "novaseq"

    @staticmethod
    def reagent_version(runtype_recognizer):
        try:
            reagent_version = runtype_recognizer.run_parameters["RunParameters"]["RfidsInfo"]["FlowCellMode"]
            return reagent_version
        except KeyError:
            raise ReagentVersionUnknown("Could not identify flowcell mode for Novaseq")


class HiSeqX(IlluminaInstrument):

    @staticmethod
    def name():
        return "hiseqx"

    @staticmethod
    def reagent_version(runtype_recognizer):
        return "v2"


class MiSeq(IlluminaInstrument):

    @staticmethod
    def name():
        return "miseq"

    @staticmethod
    def reagent_version(runtype_recognizer):
        """
        Find the reagent version used for this run, as MiSeqs can have multiple
        different reagent kit versions.

        :returns: reagent version of format v[number] e.g. v3
        """
        try:
            reagent_version = runtype_recognizer.run_parameters["RunParameters"]["ReagentKitVersion"]
            return reagent_version.replace("Version", "v")
        except KeyError:
            raise ReagentVersionUnknown("No reagent version specified for this instrument type")


class HiSeq2500(IlluminaInstrument):

    @staticmethod
    def name():
        return "hiseq2500"

    @staticmethod
    def reagent_version(runtype_recognizer):
        """
        Find run mode (rapid or not) and reagent version used for this run

        :return run mode (as specified in RunInfo.xml) and reagent version
                joint as one string e.g. rapidhighoutput_v4 or rapidrun_v2
        """
        try:
            run_mode = runtype_recognizer.run_parameters["RunParameters"]["Setup"]["RunMode"].lower()
        except KeyError:
            raise RunModeUnknown("No run mode specified for this instrument type")

        try:
            reagent_version = runtype_recognizer.run_parameters["RunParameters"]["Setup"]["Sbs"]
            #Select last element from string "HiSeq SBS Kit v4"
            format_reagent_version= reagent_version.split(" ")[-1].strip().lower()
        except KeyError:
            raise ReagentVersionUnknown("No reagent version specified for this instrument type and run mode")

        return "{}_{}".format(run_mode, format_reagent_version)


class RunTypeRecognizer(object):
    """
    RunTypeRecognizer will read files in the runfolder to determine information about the run,
    such as the instrument type, the read length, etc.

    The runfolder needs to have a 'RunInfo.xml' and a '[R|r]unParameters.xml' file.
    """

    def __init__(self, runfolder, runfolder_reader=RunfolderReader()):
        """
        Create a RunTypeRecognizer instance

        :param runfolder: to gather data about
        :param runfolder_reader: reader class for for runfolders, defaults to RunfolderReader. Here to make testing
        easier.
        """
        self._runfolder = runfolder
        self.run_info = runfolder_reader.read_run_info_xml(runfolder)
        self.run_parameters = runfolder_reader.read_run_parameters_xml(runfolder)


    def instrument_type(self):
        """
        This will look in the RunInfo.xml and determine the run type, based on the
        mappings from instrument names to instrument types

        :raises: InstrumentTypeUnknown
        :returns: the instrument type of the runfolder
        """
        instrument_name = self.run_info["RunInfo"]["Run"]["Instrument"]
        machine_type_mappings = {"M": "miseq",
                                 "D": "hiseq2500",
                                 "ST": "hiseqx",
                                 "A": "novaseq",
                                 "FS": "iseq"}

        for key, value in machine_type_mappings.items():
            if instrument_name.startswith(key):
                return IlluminaInstrument.create_instrument_instance(value)

        raise InstrumentTypeUnknown("Did not recognize instrument type of: {}".format(instrument_name))

    def instrument_and_reagent_version(self):
        """
        Get the instrument and reagent version associated with this runfolder.

        :returns: the joined instrument and reagent version, e.g. 'hiseq2500_rapidrun_v2'
        """
        instrument_type = self.instrument_type()
        return "_".join([instrument_type.name(), instrument_type.reagent_version(self)])

    def read_length(self):
        """
        Gather information on the read length of the run.

        :returns: The read length. If multiple reads delimited by "-", e.g. 150-150.
        """
        reads = self.run_info["RunInfo"]["Run"]["Reads"]["Read"]

        read_lengths = []
        for read in reads:
            if not read['@IsIndexedRead'] == 'Y':
                read_lengths.append(int(read['@NumCycles']))

        if len(read_lengths) < 1:
            raise RunModeUnknown("Found no NumCycles in RunInfo.xml, could not determine read length")

        return "-".join(map(str, read_lengths))



