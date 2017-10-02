
import json
import os

from checkQC.parsers.parser import Parser


class StatsJsonParser(Parser):

    def __init__(self, runfolder, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file_path = os.path.join(runfolder, "Unaligned", "Stats", "Stats.json")

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
