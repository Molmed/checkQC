
from qc_gate.parsers.parser import Parser


class SimpleFileParser(Parser):

    def __init__(self, file_path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file_path = file_path

    def run(self):
        with open(self.file_path, "r") as f:
            for line in f:
                for subscriber in self.subscribers:
                    subscriber.send(line)
