
import xmltodict
import os
import logging
from checkQC.exceptions import RunParametersNotFound, RunInfoXMLNotFound

log = logging.getLogger(__name__)


class RunfolderReader(object):
    """
    This class provides methods to read files such as the runParameters.xml and RunInfo.xml files, which
    often need to be read to pick up info about what type of run we are looking at etc.
    """

    @staticmethod
    def get_nbr_of_lanes(runfolder):
        runinfo_xml = RunfolderReader.read_run_info_xml(runfolder)
        return int(runinfo_xml["RunInfo"]["Run"]["FlowcellLayout"]["@LaneCount"])

    @staticmethod
    def read_run_parameters_xml(runfolder):
        """
        Read the run parameters of an Illumina instrument are recorded in a file called
        runParameters or RunParameters depending on the exact instrument type. This method
        will read it and return it as a dict.
        :param runfolder: to look in
        :return: the [R|r]unParameters.xml as a dict
        :raises: RunParametersNotFound if no [R|r]unParameters.xml was found
        """
        try:
            with open(RunfolderReader.find_run_parameters_xml(runfolder)) as f:
                return xmltodict.parse(f.read())
        except FileNotFoundError:
            raise RunParametersNotFound("Could not find [R|r]unParameters.xml for runfolder {}".format(runfolder))

    @staticmethod
    def read_run_info_xml(runfolder):
        """
        Read the RunInfo.xml and return it as a dict
        :param runfolder: to look in
        :return: RunInfo.xml data as a dict
        """
        try:
            run_info_path = os.path.join(runfolder, "RunInfo.xml")
            if not os.path.exists(run_info_path):
                log.error("Could not find a RunInfo.xml in {}. Are you sure this is a runfolder?".format(run_info_path))
                raise FileNotFoundError("Could not find {}".format(run_info_path))
            with open(run_info_path) as f:
                return xmltodict.parse(f.read())
        except FileNotFoundError:
            raise RunInfoXMLNotFound("Could not find RunInfo.xml at {}".format(run_info_path))

    @staticmethod
    def find_run_parameters_xml(runfolder):
        """
        Finds the path to the [r|R]unParameters.xml
        :param runfolder: to look in
        :return: the path to the [r|R]unParameters.xml
        """
        first_option = os.path.join(runfolder, "RunParameters.xml")
        second_option = os.path.join(runfolder, "runParameters.xml")
        if os.path.isfile(first_option):
            return first_option
        elif os.path.isfile(second_option):
            return second_option
        else:
            log.error("Could not find [R|r]unParameters.xml in directory {}. "
                      "Are you sure this is a runfolder?".format(runfolder))
            raise FileNotFoundError("Could not find [R|r]unParameters.xml for runfolder {}".format(runfolder))
