
import unittest

from checkQC.config import Config


class TestConfig(unittest.TestCase):

    def setUp(self):
        self.first_handler = {"first_handler"}
        self.second_handler = {"second_handler"}
        config_dict = {'instrument_type_mappings': {'SN': 'hiseq2000', 'M': 'miseq', 'D': 'hiseq2500', 'ST': 'hiseqx'},
                       'miseq_v3': {
                           300: {'handlers': [
                               self.first_handler]},
                           '150-299': {'handlers': [
                               self.second_handler]}
                       }}
        self.config = Config(config_dict)

    def test_exact_match(self):
        handlers = self.config.get_handler_config('miseq_v3', 300)
        self.assertListEqual(handlers, [self.first_handler])

    def test_interval_match(self):
        handlers = self.config.get_handler_config('miseq_v3', 175)
        self.assertListEqual(handlers, [self.second_handler])

    def test_no_match(self):
        with self.assertRaises(KeyError):
            self.config.get_handler_config('miseq_v3', 999)

    def test_call_with_str(self):
        handlers = self.config.get_handler_config('miseq_v3', "300")
        self.assertListEqual(handlers, [self.first_handler])

if __name__ == '__main__':
    unittest.main()
