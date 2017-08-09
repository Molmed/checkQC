
import os

import xmltodict


class InstrumentTypeUnknown(Exception):
    pass


class RunModeUnknown(Exception):
    pass


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
            self._run_info = xmltodict.parse(f.read())

    def instrument_type(self):
        """
        This will look in the RunInfo.xml and determine the run type, based on the
        mappings from instrument names to instrument types present in the config file.
        :raises: InstrumentTypeUnknown
        :return: the instrument type of the runfolder
        """
        instrument_name = self._run_info["RunInfo"]["Run"]["Instrument"]
        machine_type_mappings = self._config["instrument_type_mappings"]

        for key, value in machine_type_mappings.items():
            if instrument_name.startswith(key):
                return value

        raise InstrumentTypeUnknown("Did not recognize instrument type of: {}".format(instrument_name))

    def read_length(self):
        """
        Gathers information on the read length of the run.
        :return: The read length. If multiple reads delimited by "-"
        """
        reads = self._run_info["RunInfo"]["Run"]["Reads"]["Read"]

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



