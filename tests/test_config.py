
import unittest

from checkQC.config import Config, ConfigFactory

from checkQC.exceptions import ConfigEntryMissing


class TestConfig(unittest.TestCase):

    def setUp(self):
        self.first_handler = {"name": "first_handler"}
        self.second_handler = {"name": "second_handler"}
        self.third_handler = {"name": "third_handler", "warning": "unknown", "error": 100}
        self.default_handler = {"name": "default_handler", "config": "some_value"}
        config_dict = {'instrument_type_mappings': {'SN': 'hiseq2000', 'M': 'miseq', 'D': 'hiseq2500', 'ST': 'hiseqx'},
                       'miseq_v3': {
                           300: {'handlers': [
                               self.first_handler]},
                           '150-299': {'handlers': [
                               self.second_handler]}
                       },
                       'hiseqx': {
                           50: {'handlers': [
                               self.first_handler]},
                           52: {'handlers': [
                               self.second_handler]}
                       },
                       "default_handlers": [
                           self.default_handler,
                           self.first_handler
                       ],
                       "extra_key": "extra_value"}
        self.config = Config(config_dict)

    def test_exact_match(self):
        handlers = self.config.get_handler_configs('miseq_v3', 300)
        self.assertListEqual(handlers, [self.first_handler, self.default_handler])

    def test_interval_match(self):
        handlers = self.config.get_handler_configs('miseq_v3', 175)
        self.assertListEqual(handlers, [self.second_handler, self.default_handler, self.first_handler])

    def test_no_match(self):
        with self.assertRaises(ConfigEntryMissing):
            self.config.get_handler_configs('miseq_v3', 999)

    def test_call_with_str(self):
        handlers = self.config.get_handler_configs('miseq_v3', "300")
        self.assertListEqual(handlers, [self.first_handler, self.default_handler])

    def test_get(self):
        self.assertEqual(self.config.get("extra_key"), "extra_value")
        self.assertEqual(self.config.get("this_key_does_not_exist", "default"), "default")
        self.assertEqual(self.config.get("this_key_does_not_exist"), None)

    def test_downgrade_errors(self):
        handler_list = [self.first_handler, self.third_handler]
        result = self.config._downgrade_errors(handler_list, ("third_handler"))
        self.assertEqual(len(result), len(handler_list))
        self.assertEqual(result[1]["error"], "unknown")
        self.assertEqual(result[1]["warning"], 100)

    def test_use_closest_read_length(self):
        result = self.config._get_matching_handler('miseq_v3', 149, use_closest_read_length=True)
        self.assertEqual(result, [self.second_handler])

    def test_use_closest_read_length_in_the_middle(self):
        result = self.config._get_matching_handler('hiseqx', 51, use_closest_read_length=True)
        self.assertEqual(result, [self.second_handler])

    def test_machine_and_reagent_type_not_found(self):
        with self.assertRaises(ConfigEntryMissing):
            self.config._get_matching_handler('foo', 51, use_closest_read_length=True)


class TestConfigFactory(unittest.TestCase):

    def test_get_logging_config_file_default(self):
        result = ConfigFactory.get_logging_config_dict(None)
        default_config = {'version': 1, 'disable_existing_loggers': False,
                          'formatters':
                              {'simple': {'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'}},
                          'handlers':
                              {'console':
                                   {'class': 'logging.StreamHandler', 'level': 'INFO', 'formatter': 'simple',
                                    'stream': 'ext://sys.stdout'},
                               'file_handler': {'class': 'logging.handlers.RotatingFileHandler', 'level': 'INFO',
                                                'formatter': 'simple', 'filename': 'checkqc-ws.log',
                                                'maxBytes': 10485760, 'backupCount': 20,
                                                'encoding': 'utf8'}},
                          'root':
                              {'level': 'INFO', 'handlers': ['console', 'file_handler']}}
        self.assertEqual(result, default_config)


if __name__ == '__main__':
    unittest.main()
