
import yaml


def get_config(config_file):
    with open(config_file) as stream:
        config = yaml.load(stream)
    return config
