
import json
import os
import logging

from checkQC.parsers.parser import Parser
from checkQC.exceptions import StatsJsonNotFound

log = logging.getLogger(__name__)


class StatsJsonParser(Parser):

    def __init__(self, runfolder, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file_path = os.path.join(runfolder, "Unaligned", "Stats", "Stats.json")
        if not os.path.exists(self.file_path):
            log.error("Could not identify a Stats.json file at: {}. This file is "
                      "created by bcl2fastq, please ensure that you have run "
                      "bcl2fastq on this runfolder before running checkqc.".format(self.file_path))
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
