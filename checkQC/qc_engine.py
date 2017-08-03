
from collections import defaultdict
from checkQC.handlers.qc_handler import QCHandler


class QCEngine(object):

    def __init__(self, runfolder, handler_config):
        self.runfolder = runfolder
        self.handlers_config = handler_config
        self.handlers = []
        self.parsers = defaultdict(list)
        self.exit_status = 0

    def run(self):
        self.create_handlers()
        self.initiate_parsers()
        self.subscribe_handlers_to_parsers()
        self.run_parsers()
        self.compile_reports()

    def create_handlers(self):
        for clazz_config in self.handlers_config:
            self.handlers.append(QCHandler.create_subclass_instance(clazz_config["name"], clazz_config))

    def initiate_parsers(self):
        for handler in self.handlers:
            parser_factory = handler.parser()
            parser_instance = parser_factory(self.runfolder)
            self.parsers[parser_instance].append(handler)

    def subscribe_handlers_to_parsers(self):
        for parser, handlers in self.parsers.items():
            parser.add_subscribers(handlers)

    def run_parsers(self):
        for parser in self.parsers:
            parser.run()

    def compile_reports(self):
        for handler in self.handlers:
            handler.report()
            if handler.exit_status != 0:
                self.exit_status = 1
