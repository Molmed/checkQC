from unittest import TestCase
from mock import create_autospec, MagicMock

from checkQC.qc_engine import QCEngine
from checkQC.handlers.qc_handler_factory import QCHandlerFactory
from checkQC.handlers.q30_handler import Q30Handler
from checkQC.handlers.undetermined_percentage_handler import UndeterminedPercentageHandler
from checkQC.parsers.parser import Parser
from checkQC.exceptions import ConfigurationError

class TestQCEngine(TestCase):

    class FakeParser(Parser):

        def __init__(self, runfolder, parser_configurations, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.has_been_run = False

        def run(self):
            self.has_been_run = True
            self._send_to_subscribers("Fake value!")

        def __eq__(self, other):
            if isinstance(other, self.__class__):
                return True
            else:
                return False

        def __hash__(self):
            return hash(self.__class__.__name__)

    def setUp(self):
        runfolder = "foo"
        handler_config = [{'name': 'Q30Handler', 'warning': 30, 'error': 20},
                          {'name': 'UndeterminedPercentageHandler', 'warning': 0.01, 'error': 0.02}]

        parser_configurations = {"StatsJsonParser": {"bcl2fastq_output_path": "foo/"}}

        self.mock_q30_handler = create_autospec(Q30Handler)
        self.mock_q30_handler.parser.return_value = self.FakeParser

        self.mock_undetermined_perc_handler = create_autospec(UndeterminedPercentageHandler)
        self.mock_undetermined_perc_handler.parser.return_value = self.FakeParser

        self.handlers = [self.mock_q30_handler, self.mock_undetermined_perc_handler]
        self.parsers_and_handlers = {self.FakeParser(runfolder, parser_configurations): self.handlers}

        qc_handler_factory_mock = create_autospec(QCHandlerFactory)
        qc_handler_factory_mock.create_subclass_instance.side_effect = self.handlers

        self.qc_engine = QCEngine(runfolder=runfolder,
                                  handler_config=handler_config,
                                  parser_configurations=parser_configurations,
                                  qc_handler_factory=qc_handler_factory_mock)

    def test__create_handlers(self):
        self.qc_engine._create_handlers()
        self.assertListEqual(self.qc_engine._handlers, self.handlers)

    def test__initiate_parsers(self):
        self.qc_engine._handlers = self.handlers

        self.qc_engine._initiate_parsers()

        self.assertTrue(len(self.qc_engine._parsers_and_handlers.keys()) == 1)
        self.assertTrue(len(self.qc_engine._parsers_and_handlers.values()) == 1)
        self.assertListEqual(list(self.qc_engine._parsers_and_handlers.values())[0], self.handlers)

    def test__validate_configurations_all_ok(self):
        self.qc_engine._handlers = self.handlers
        self.qc_engine._parsers_and_handlers = self.parsers_and_handlers
        result = self.qc_engine._validate_configurations()
        self.assertTrue(result)

    def test__validate_configurations_has_problem(self):
        self.qc_engine._handlers = self.handlers
        self.qc_engine._parsers_and_handlers = self.parsers_and_handlers
        self.mock_q30_handler.validate_configuration.side_effect = ConfigurationError
        with self.assertRaises(ConfigurationError):
            self.qc_engine._validate_configurations()

    def test__subscribe_handlers_to_parsers(self):
        self.qc_engine._handlers = self.handlers
        self.qc_engine._parsers_and_handlers = self.parsers_and_handlers

        self.qc_engine._subscribe_handlers_to_parsers()

        parser = list(self.qc_engine._parsers_and_handlers.keys())[0]
        self.assertListEqual(parser.subscribers, self.handlers)

    def test__run_parsers(self):
        self.qc_engine._handlers = self.handlers
        self.qc_engine._parsers_and_handlers = self.parsers_and_handlers

        for parser, handlers in self.parsers_and_handlers.items():
            parser.add_subscribers(handlers)

        self.qc_engine._run_parsers()

        for parser in self.qc_engine._parsers_and_handlers.keys():
            self.assertTrue(parser.has_been_run)

    def test__compile_reports(self):

        self.qc_engine._handlers = self.handlers

        self.mock_q30_handler.exit_status.return_value = 0
        self.mock_undetermined_perc_handler.exit_status.return_value = 0
        self.qc_engine._compile_reports()
        self.assertEqual(self.qc_engine.exit_status, 0)

        self.mock_q30_handler.exit_status.return_value = 0
        self.mock_undetermined_perc_handler.exit_status.return_value = 1
        self.qc_engine._compile_reports()
        self.assertEqual(self.qc_engine.exit_status, 1)

        self.mock_q30_handler.exit_status.return_value = 1
        self.mock_undetermined_perc_handler.exit_status.return_value = 0
        self.qc_engine._compile_reports()
        self.assertEqual(self.qc_engine.exit_status, 1)

    def test_run_exit_status_0(self):

        self.mock_q30_handler.exit_status.return_value = 0
        self.mock_undetermined_perc_handler.exit_status.return_value = 0
        self.qc_engine.run()
        for parser in self.qc_engine._parsers_and_handlers.keys():
            self.assertTrue(parser.has_been_run)

        self.assertEqual(self.qc_engine.exit_status, 0)

    def test_run_exit_status_1(self):
        self.mock_q30_handler.exit_status.return_value = 1
        self.mock_undetermined_perc_handler.exit_status.return_value = 0
        self.qc_engine.run()
        for parser in self.qc_engine._parsers_and_handlers.keys():
            self.assertTrue(parser.has_been_run)

        self.assertEqual(self.qc_engine.exit_status, 1)

    def test_run_with_config_error(self):
        self.mock_q30_handler.validate_configuration.side_effect = ConfigurationError
        self.qc_engine.run()
        self.assertEqual(self.qc_engine.exit_status, 1)
