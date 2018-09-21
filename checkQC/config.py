
from pkg_resources import Requirement, resource_filename
import logging
from checkQC.exceptions import ConfigEntryMissing

import yaml


log = logging.getLogger(__name__)


class ConfigFactory(object):
    """
    The ConfigFactory provides methods for creating a Config instance.
    """

    @staticmethod
    def from_config_path(config_path):
        """
        Creates a Config instance from the provided config_path

        :param config_path: path to the configuration, or None. If no config_path is provided the default config file will be used \
        :returns: Config instance based on the specified file path
        """
        config_file_content = ConfigFactory._get_config_file(config_path)
        return Config(config_file_content)

    @staticmethod
    def _get_config_file(config_path):
        """
        Load the content of the config file. If no config_path is specified, get the default of config file.

        :param config_path: path to the config file or None
        :returns: the content of the config file
        """
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
        """
        Loads the specified logger config. This is useful when CheckQC is used more like a library, so that the
        default logging configuration can be overridden.

        :param config_path: Path to the logging config.
        :returns: The content of the logging config file.
        """
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
    """
    A Config object wraps the configuration for all handlers, so that the correct config can be passed to a handler
    depending on e.g. which read length and run type has been used for a sequencing run.
    """

    def __init__(self, config):
        """
        Create a Config instance.

        :param config: content of the config file
        """
        self._config = config

    def _get_matching_handler(self, instrument_and_reagent_type, read_length):
        """
        Get the handler matching the provided parameters.

        :param instrument_and_reagent_type: the instrument and run type, e.g. 'hiseq2500_rapidhighoutput_v4'
        :param read_length: either as a range, e.g. '50-70' or a single value, e.g. '50'
        :returns: A dict corresponding to the handler config
        :raises: ConfigEntryMissing if instrument, reagent type and read length detected is missing from config
        """

        try:
            config_read_lengths = list(map(str, self._config[instrument_and_reagent_type].keys()))

            for config_read_length in config_read_lengths:
                if "-" in config_read_length:
                    split_read_length = config_read_length.split("-")
                    low_break = int(split_read_length[0])
                    high_break = int(split_read_length[1])
                    if low_break <= int(read_length) <= high_break:
                        return self._config[instrument_and_reagent_type][config_read_length]["handlers"]
                else:
                    if int(read_length) == int(config_read_length):
                        return self._config[instrument_and_reagent_type][int(config_read_length)]["handlers"]
            raise ConfigEntryMissing("Could not find a config entry matching read length '{}' on "
                                     "instrument '{}'. Please check the provided "
                                     "config.".format(read_length, instrument_and_reagent_type))
        except KeyError:
            raise ConfigEntryMissing("Could not find a config entry for instrument '{}' "
                                     "with read length '{}'. Please check the provided config "
                                     "file ".format(instrument_and_reagent_type,
                                                    read_length))

    def _add_default_config(self, current_handler_config):
        """
        Add the default handlers specified in the config.

        :param current_handler_config: a list of handlers. This will be mutated.
        :returns: The provided list with the default configs added to it.
        """

        current_handler_names = set(map(lambda x: x["name"], current_handler_config))
        default_handlers = self._config["default_handlers"]
        for default_handler in default_handlers:
            if not default_handler["name"] in current_handler_names:
                current_handler_config.append(default_handler)
        return current_handler_config

    def get_handler_configs(self, instrument_and_reagent_type, read_length):
        """
        Get the handler configurations for the specified parameters.

        :param instrument_and_reagent_type: type of instrument and reagents to match from config
        :param read_length: give the read length either as str or int
        :returns: the corresponding handler configuration(s)
        """

        try:
            handler_config = self._get_matching_handler(instrument_and_reagent_type, read_length)
            handler_config_with_defaults = self._add_default_config(handler_config)
            return handler_config_with_defaults
        except ConfigEntryMissing as e:
            log.error("Could not find a config entry for instrument '{}' "
                      "with read length '{}'. Please check the provided config "
                      "file ".format(instrument_and_reagent_type,
                                     read_length))
            raise e

    def __getitem__(self, key):
        return self._config[key]

    def get(self, key, default=None):
        try:
            return self.__getitem__(key)
        except KeyError:
            return default
