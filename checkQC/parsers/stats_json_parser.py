
import json
import os
import logging

from checkQC.parsers.parser import Parser
from checkQC.exceptions import StatsJsonNotFound, ConfigurationError

log = logging.getLogger(__name__)


class StatsJsonParser(Parser):
    """
    The StatsJsonParser reads the values from the Illumina Stats.json file (which is created by bcl2fastq) and sends
    each key value pair as a tuple to the subscribers, e.g.:

        ('Flowcell', 'CB1TVANXX')
        ('RunNumber', 303)
        ('RunId', '170726_D00118_0303_BCB1TVANXX')

    The subscribers decide which of these values they are iterested in.
    """

    def __init__(self, runfolder, parser_configurations, *args, **kwargs):
        """
        Create a StatsJsonParser instance for the specified runfolder
        :param runfolder: path to the runfolder to parse
        :param parser_configurations: dict containing any extra configuration required by
        the parser under class name key
        """
        super().__init__(*args, **kwargs)

        self.parser_conf = parser_configurations.get(self.__class__.__name__)
        if not self.parser_conf:
            raise ConfigurationError("The configuration must contain parser_configurations "
                                     "key with subkey StatsJsonParser. E.g: \n"
                                     "parser_configurations:\n"
                                     "\tStatsJsonParser:\n"
                                     "\t\tbcl2fastq_output_path: Data/Intensities/BaseCalls")

        bcl2fastq_output_path = self.parser_conf.get("bcl2fastq_output_path")
        if not bcl2fastq_output_path:
            raise ConfigurationError("The configuration must contain the key bcl2fastq_output_path, specifying "
                                     "where the bcl2fastq output is, relative to the runfolder root.")

        self.file_path = os.path.join(runfolder, bcl2fastq_output_path, "Stats", "Stats.json")
        if not os.path.exists(self.file_path):
            log.error("Could not identify a Stats.json file at: {}. This file is "
                      "created by bcl2fastq, please ensure that you have run "
                      "bcl2fastq on this runfolder before running checkqc."
                      "If this file is not located under <RUNFOLDER>/Data/Intensities/BaseCalls/Stats/Stats.json "
                      "which is the default option for bcl2fastq, you can specify where the 'Stats' directory is "
                      "located by changing the 'bcl2fastq_output_path' in the 'StatsJsonParser' part of the "
                      "checkqc configuration file.".format(self.file_path))
            raise StatsJsonNotFound("Could not find a Stats.json file at: {}".format(self.file_path))

    def run(self):
        with open(self.file_path, "r") as f:
            data = json.load(f)
            for key_value in data.items():
                self._send_to_subscribers(key_value)

    def __eq__(self, other):
        if isinstance(other, self.__class__) and self.file_path == other.file_path:
            return True
        else:
            return False

    def __hash__(self):
        return hash(self.__class__.__name__ + self.file_path)
