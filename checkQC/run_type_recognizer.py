
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
        # TODO This is where to figure out if this is a rapid, reagent version etc...
        raise NotImplementedError()


class HiSeq2000(IlluminaInstrument):

    @staticmethod
    def name():
        return "hiseq2000"

    @staticmethod
    def reagent_version(runtype_recognizer):
        # TODO This is where to figure out if this is a rapid, reagent version etc...
        raise NotImplementedError()


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
        mappings from instrument names to instrument types present in the config file.
        :raises: InstrumentTypeUnknown
        :return: the instrument type of the runfolder
        """
        instrument_name = self.run_info["RunInfo"]["Run"]["Instrument"]
        machine_type_mappings = self._config["instrument_type_mappings"]

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



