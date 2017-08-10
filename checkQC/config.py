
from pkg_resources import Requirement, resource_filename

import yaml


def get_config(config_path):
    try:
        if not config_path:
            config_path = resource_filename(Requirement.parse('checkQC'), 'checkQC/default_config/config.yaml')
            print("No config file specified, using default config from {}.".format(config_path))

        with open(config_path) as stream:
            return yaml.load(stream)
    except FileNotFoundError as e:
        print("Could not find config file: {}".format(e))
        raise e


def get_handler_config(config, instrument_and_reagent_type, read_length):
    try:
        handler_config = config[instrument_and_reagent_type][read_length]["handlers"]
        return handler_config
    except KeyError as e:
        print("Could not find a config entry for instrument '{}' "
              "with read length '{}'. Please check the provided config "
              "file ".format(instrument_and_reagent_type,
                             read_length))
        raise e
