
import json

from qc_gate.parsers.parser import Parser


class StatsJsonParser(object):

    class __StatsJsonParser(Parser):

        def __init__(self, file_path, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.file_path = file_path

        def run(self):
            with open(self.file_path, "r") as f:
                data = json.load(f)
                for key_value in data.items():
                    self._send_to_subscribers(key_value)

    instance = None

    def __init__(self, file_path, *args, **kwargs):
        if not StatsJsonParser.instance:
            StatsJsonParser.instance = StatsJsonParser.__StatsJsonParser(file_path, *args, **kwargs)

    def __getattr__(self, name):
        return getattr(self.instance, name)
