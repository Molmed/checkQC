
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

    def single_or_paired_end(self):
        """
        Attempts to determine if the run has been run as single or paired end run.
        :return: "single_end" or "paired_end"
        :raises: RunModeUnknown
        """
        reads = self._run_info["RunInfo"]["Run"]["Reads"]["Read"]
        nbr_of_reads = len(reads)
        if nbr_of_reads == 1:
            return "single_end"
        elif nbr_of_reads == 2:
            return "paired_end"
        else:
            raise RunModeUnknown("Did not recognize {} number of reads as a valid run type".format(nbr_of_reads))

    def read_length(self):
        """
        Gathers information on the read length of the run.
        :return: The read length. If multiple reads delimited by "-"
        """
        reads = self._run_info["RunInfo"]["Run"]["Reads"]["Read"]

        read_lengths = []
        for read in reads:
            if not read['@IsIndexedRead'] == 'Y':
                #TODO unsure about the -1 here...
                read_lengths.append(int(read['@NumCycles']) - 1)

        if len(read_lengths) < 1:
            raise RunModeUnknown("Found no NumCycles in RunInfo.xml, could not determine read length")

        return "-".join(map(str, read_lengths))



