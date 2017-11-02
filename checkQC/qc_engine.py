
from collections import defaultdict
import logging

from checkQC.handlers.qc_handler_factory import QCHandlerFactory
from checkQC.config import ConfigurationError

log = logging.getLogger(__name__)


class QCEngine(object):

    def __init__(self, runfolder, handler_config, qc_handler_factory=None):
        self.runfolder = runfolder
        self.handlers_config = handler_config
        self._handlers = []
        self._parsers_and_handlers = defaultdict(list)
        self.exit_status = 0
        if qc_handler_factory:
            self._qc_handler_factory = qc_handler_factory
        else:
            self._qc_handler_factory = QCHandlerFactory()

    def run(self):
        try:
            self._create_handlers()
            self._validate_configurations()
            self._initiate_parsers()
            self._subscribe_handlers_to_parsers()
            self._run_parsers()
            reports = self._compile_reports()
            return reports
        except ConfigurationError:
            self.exit_status = 1

    def _create_handlers(self):
        for clazz_config in self.handlers_config:
            self._handlers.append(self._qc_handler_factory.
                                  create_subclass_instance(clazz_config["name"], clazz_config))

    def _validate_configurations(self):
        try:
            for handler in self._handlers:
                handler.validate_configuration()
            return True
        except ConfigurationError as e:
            log.error("Error in configuration found for handler: {}. {}".format(type(handler).__name__, e))
            raise e

    def _initiate_parsers(self):
        for handler in self._handlers:
            parser_factory = handler.parser()
            parser_instance = parser_factory(self.runfolder)
            self._parsers_and_handlers[parser_instance].append(handler)

    def _subscribe_handlers_to_parsers(self):
        for parser, handlers in self._parsers_and_handlers.items():
            parser.add_subscribers(handlers)

    def _run_parsers(self):
        for parser in self._parsers_and_handlers.keys():
            parser.run()

    def _compile_reports(self):
        reports = {"exit_status": 0}
        for handler in self._handlers:
            handler_report = handler.report()
            if handler_report:
                reports[type(handler).__name__] = list(map(lambda x: x.as_dict(), handler_report))
            if handler.exit_status() != 0:
                self.exit_status = 1
                reports["exit_status"] = 1
        return reports
