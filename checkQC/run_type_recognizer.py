
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


class NovaSeqXPlus(IlluminaInstrument):

    @staticmethod
    def name():
        return "novaseqxplus"

    @staticmethod
    def reagent_version(runtype_recognizer):
        try:
            run_parameters = runtype_recognizer.run_parameters['RunParameters']
            consumables = run_parameters["ConsumableInfo"]["ConsumableInfo"]
            reagent_version = next(
                consumable for consumable in consumables
                if consumable['Type'] == 'FlowCell'
            )['Mode']
            return reagent_version
        except (KeyError, StopIteration):
            raise ReagentVersionUnknown("Could not identify flowcell mode for NovaSeqXPlus")


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
        Find the reagent kit version (and flowcell mode if applicable) for this run

        :returns: reagent version in format v[reagent kit version] or [flowcell mode]_v[reagent kit version],
         e.g. v3 or nano_v2
        """
        def _reagent_kit_version(runtype_recognizer):
            try:
                reagent_version = runtype_recognizer.run_parameters["RunParameters"]["ReagentKitVersion"]
                return reagent_version.replace("Version", "v")
            except KeyError:
                raise ReagentVersionUnknown("No reagent version specified for this instrument type")

        def _flowcell_type(runtype_recognizer):
            try:
                tiles_per_swath = int(runtype_recognizer.run_parameters["RunParameters"]["Setup"]["NumTilesPerSwath"])
                match tiles_per_swath:
                    case 2:
                        return "nano"
                    case 4:
                        return "micro"
                    case x if x >= 14:
                        return "standard"
                    case _:
                        raise ReagentVersionUnknown()
            except (KeyError, ReagentVersionUnknown):
                raise ReagentVersionUnknown("Unable to identify flowcell type through number of tiles per swath")

        flowcell_version = _flowcell_type(runtype_recognizer)
        reagent_version = _reagent_kit_version(runtype_recognizer)
        if flowcell_version == "standard":
            return reagent_version
        else:
            return "_".join([flowcell_version, reagent_version])


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
        machine_type_mappings = {
            "M": MiSeq,
            "D": HiSeq2500,
            "ST": HiSeqX,
            "A": NovaSeq,
            "FS": ISeq,
            "LH": NovaSeqXPlus,
        }

        for instrument_code, instrument_class in machine_type_mappings.items():
            if instrument_name.upper().startswith(instrument_code):
                return instrument_class()

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
