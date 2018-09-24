
from collections import defaultdict
import logging

from checkQC.handlers.qc_handler_factory import QCHandlerFactory
from checkQC.exceptions import ConfigurationError

log = logging.getLogger(__name__)


class QCEngine(object):
    """
    The QCEngine will provide a method to apply all specified handler on the specified runfolder.

    Internally it will run a number of methods which will do the following:
     - create all handlers specified in the handler config
     - validate all the configs provided, so that all necessary values are preset
     - initiate the parsers based on which parsers are found in the handlers
     - connect the handlers and parsers so that each parser gets the correct
       subscribers
     - run the parsers, i.e. pick up data and pass it to the handlers
     - compile all reports from the handlers

    The QCEngine has a `exit_status` field which can be checked after calling the `run` method,
    to determine if all handlers were successful or not (zero indicates success, 1 indicates failure)
    """

    def __init__(self, runfolder, parser_configurations, handler_config, qc_handler_factory=None):
        """
        Create a instance of QCEngine

        :param runfolder: the path to the runfolder which should be analyzed
        :param parser_configurations: dict containing configurations for the parsers
        :param handler_config: a dict which configurations for the handlers
        :param qc_handler_factory: A QCHandlerFactory, if None default QCHandlerFactory will be used
        """
        self.runfolder = runfolder
        self.parser_configurations = parser_configurations
        self.handlers_config = handler_config
        self._handlers = []
        self._parsers_and_handlers = defaultdict(list)
        self.exit_status = 0
        if qc_handler_factory:
            self._qc_handler_factory = qc_handler_factory
        else:
            self._qc_handler_factory = QCHandlerFactory()

    def run(self):
        """
        Run the specified parsers and handlers and compile their reports. Will set the `exit_status` depending
         on if there were any errors or not.

        :return: a dict representing the reports gathers.
        """
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
            if isinstance(handler.parser(), list):
                parsers = handler.parser()
            else:
                parsers = [handler.parser()]

            for parser_factory in parsers:
                parser_instance = parser_factory(runfolder=self.runfolder,
                                                 parser_configurations=self.parser_configurations)
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
