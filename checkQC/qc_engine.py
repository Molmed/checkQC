
from collections import defaultdict
from checkQC.handlers.qc_handler import QCHandler


class QCEngine(object):

    def __init__(self, runfolder, handler_config):
        self.runfolder = runfolder
        self.handlers_config = handler_config
        self._handlers = []
        self._parsers = defaultdict(list)
        self.exit_status = 0

    def run(self):
        self._create_handlers()
        self._initiate_parsers()
        self._subscribe_handlers_to_parsers()
        self._run_parsers()
        self._compile_reports()

    def _create_handlers(self):
        for clazz_config in self.handlers_config:
            self._handlers.append(QCHandler.create_subclass_instance(clazz_config["name"], clazz_config))

    def _initiate_parsers(self):
        for handler in self._handlers:
            parser_factory = handler.parser()
            parser_instance = parser_factory(self.runfolder)
            self._parsers[parser_instance].append(handler)

    def _subscribe_handlers_to_parsers(self):
        for parser, handlers in self._parsers.items():
            parser.add_subscribers(handlers)

    def _run_parsers(self):
        for parser in self._parsers:
            parser.run()

    def _compile_reports(self):
        for handler in self._handlers:
            handler.report()
            if handler.exit_status != 0:
                self.exit_status = 1
