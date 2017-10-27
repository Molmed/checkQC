
import os

import xmltodict


class InstrumentTypeUnknown(Exception):
    pass


class RunModeUnknown(Exception):
    pass


class ReagentVersionUnknown(Exception):
    pass


class IlluminaInstrument(object):

    @staticmethod
    def get_subclasses():
        return IlluminaInstrument.__subclasses__()

    @staticmethod
    def create_instrument_instance(instrument_name):
        subclasses = IlluminaInstrument.get_subclasses()
        for subclass in subclasses:
            if instrument_name == subclass.name():
                return subclass()


class NovaSeq(IlluminaInstrument):

    @staticmethod
    def name():
        return "novaseq"

    @staticmethod
    def reagent_version(runtype_recognizer):
        return "v1"


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
        Find the reagent version used for this run
        :return: reagent version of format v[number] e.g. v3
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
    """

    def __init__(self, config, runfolder):
        """

        :param config: dictionary containing the app configuration
        :param runfolder: to gather data about
        """
        self._config = config
        self._runfolder = runfolder
        with open(os.path.join(self._runfolder, "RunInfo.xml")) as f:
            self.run_info = xmltodict.parse(f.read())

        with open(self._find_run_parameters_xml()) as f:
            self.run_parameters = xmltodict.parse(f.read())

    def _find_run_parameters_xml(self):
        first_option = os.path.join(self._runfolder, "RunParameters.xml")
        second_option = os.path.join(self._runfolder, "runParameters.xml")
        if os.path.isfile(first_option):
            return first_option
        elif os.path.isfile(second_option):
            return second_option
        else:
            raise FileNotFoundError("Could not find [R|r]unParameters.xml for runfolder {}".format(self._runfolder))

    def instrument_type(self):
        """
        This will look in the RunInfo.xml and determine the run type, based on the
        mappings from instrument names to instrument types
        :raises: InstrumentTypeUnknown
        :return: the instrument type of the runfolder
        """
        instrument_name = self.run_info["RunInfo"]["Run"]["Instrument"]
        machine_type_mappings = {"M": "miseq",
                                 "D": "hiseq2500",
                                 "ST": "hiseqx",
                                 "A": "novaseq"}

        for key, value in machine_type_mappings.items():
            if instrument_name.startswith(key):
                return IlluminaInstrument.create_instrument_instance(value)

        raise InstrumentTypeUnknown("Did not recognize instrument type of: {}".format(instrument_name))

    def instrument_and_reagent_version(self):
        instrument_type = self.instrument_type()
        return "_".join([instrument_type.name(), instrument_type.reagent_version(self)])

    def read_length(self):
        """
        Gathers information on the read length of the run.
        :return: The read length. If multiple reads delimited by "-"
        """
        reads = self.run_info["RunInfo"]["Run"]["Reads"]["Read"]

        read_lengths = []
        for read in reads:
            if not read['@IsIndexedRead'] == 'Y':
                # The -1 is necessary for the number of cycles to correspond to the
                # way it is specified in the docs. I.e. read length 300 in the docs
                # means 301 cycles were run...
                read_lengths.append(int(read['@NumCycles']) - 1)

        if len(read_lengths) < 1:
            raise RunModeUnknown("Found no NumCycles in RunInfo.xml, could not determine read length")

        return "-".join(map(str, read_lengths))



