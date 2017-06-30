
from qc_gate.handlers.qc_handler import QCHandler


class QCEngine(object):

    def __init__(self, runfolder):
        self.runfolder = runfolder
        self.handlers = []
        self.parsers = set()
        self.exit_status = 0

    def create_handlers(self, handlers, runfolder):
        self.runfolder = runfolder
        for clazz_config in handlers:
            self.handlers.append(QCHandler.create_subclass_instance(clazz_config["name"]))

    def initiate_parsers(self):
        for handler in self.handlers:
            parser = handler.initiate_parser(self.runfolder)
            self.parsers.add(parser)

    def run(self):
        for parser in self.parsers:
            parser.run()

    def compile_reports(self):
        for handler in self.handlers:
            handler.report()
            if handler.exit_status != 0:
                self.exit_status = 1
