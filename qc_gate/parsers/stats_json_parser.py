
import json
import os

from qc_gate.parsers.parser import Parser


class StatsJsonParser(object):

    class __StatsJsonParser(Parser):

        def __init__(self, runfolder, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Update this to reflect the actual place where the file should like
            self.file_path = os.path.join(runfolder, "Stats.json")
            self.has_executed = False

        def run(self):
            if not self.has_executed:
                with open(self.file_path, "r") as f:
                    data = json.load(f)
                    for key_value in data.items():
                        self._send_to_subscribers(key_value)
                self.has_executed = True

    instance = None

    def __init__(self, runfolder, *args, **kwargs):
        if not StatsJsonParser.instance:
            StatsJsonParser.instance = StatsJsonParser.__StatsJsonParser(runfolder, *args, **kwargs)

    def __getattr__(self, name):
        return getattr(self.instance, name)

