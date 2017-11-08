
from pkg_resources import Requirement, resource_filename
import logging

import yaml

log = logging.getLogger(__name__)


class ConfigurationError(Exception):
    pass


class ConfigFactory(object):

    @staticmethod
    def from_config_path(config_path):
        config_file_content = ConfigFactory._get_config_file(config_path)
        return Config(config_file_content)

    @staticmethod
    def _get_config_file(config_path):
        try:
            if not config_path:
                config_path = resource_filename(Requirement.parse('checkQC'), 'checkQC/default_config/config.yaml')
                log.info("No config file specified, using default config from {}.".format(config_path))

            with open(config_path) as stream:
                return yaml.load(stream)
        except FileNotFoundError as e:
            log.error("Could not find config file: {}".format(e))
            raise e

    @staticmethod
    def get_logging_config_dict(config_path):
        try:
            if not config_path:
                config_path = resource_filename(Requirement.parse('checkQC'), 'checkQC/default_config/logger.yaml')
                log.info("No logging config file specified, using default config from {}.".format(config_path))
            with open(config_path) as stream:
                return yaml.load(stream)
        except FileNotFoundError as e:
            log.error("Could not find config file: {}".format(e))
            raise e


class Config(object):

    def __init__(self, config):
        self._config = config

    def _get_matching_handler(self, instrument_and_reagent_type, read_length):
        config_read_lengths = list(map(str, self._config[instrument_and_reagent_type].keys()))
        for config_read_length in config_read_lengths:
            if "-" in config_read_length:
                split_read_length = config_read_length.split("-")
                low_break = int(split_read_length[0])
                high_break = int(split_read_length[1])
                if low_break < int(read_length) <= high_break:
                    return self._config[instrument_and_reagent_type][config_read_length]["handlers"]
            else:
                if int(read_length) == int(config_read_length):
                    return self._config[instrument_and_reagent_type][int(config_read_length)]["handlers"]
        raise KeyError

    def _add_default_config(self, current_handler_config):

        current_handler_names = set(map(lambda x: x["name"], current_handler_config))
        default_handlers = self._config["default_handlers"]
        for default_handler in default_handlers:
            if not default_handler["name"] in current_handler_names:
                current_handler_config.append(default_handler)
        return current_handler_config

    def get_handler_config(self, instrument_and_reagent_type, read_length):
        """
        :param instrument_and_reagent_type: type of instrument and reagents to match from config
        :param read_length: give the read length either as str or int
        :return: the corresponding handler configuration(s)
        """
        try:
            handler_config = self._get_matching_handler(instrument_and_reagent_type, read_length)
            handler_config_with_defaults = self._add_default_config(handler_config)
            return handler_config_with_defaults
        except KeyError as e:
            log.error("Could not find a config entry for instrument '{}' "
                      "with read length '{}'. Please check the provided config "
                      "file ".format(instrument_and_reagent_type,
                                     read_length))
            raise e

    def __getitem__(self, item):
        return self._config[item]
