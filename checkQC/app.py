
import sys
import os

import click

from checkQC.qc_engine import QCEngine
from checkQC.config import get_config
from checkQC.run_type_recognizer import RunTypeRecognizer

from pkg_resources import Requirement, resource_filename

@click.command("checkQC")
@click.option("--config_file", help="Path to the checkQC configuration file", type=click.Path())
@click.argument('runfolder', type=click.Path())
def start(config_file, runfolder):
    """
    checkQC is a command line utility designed to quickly gather and assess quality control metrics from a
    Illumina sequencing run. It is highly customizable and which quality controls modules should be run
    for a particular run type should be specified in the provided configuration file.
    """

    try:
        if not config_file:
            config_file = resource_filename(Requirement.parse('checkQC'), 'checkQC/default_config/config.yaml')
            print("No config file specified, using default config from {}.".format(config_file))
            config = get_config(config_file)
    except FileNotFoundError as e:
        print("Could not find config file: {}".format(e))
        sys.exit(1)

    run_type_recognizer = RunTypeRecognizer(config=config, runfolder=runfolder)
    instrument_type = run_type_recognizer.instrument_type()
    read_length = run_type_recognizer.read_length()

    try:
        handler_config = config[instrument_type][read_length]["handlers"]
    except KeyError:
        print("Could not find a config entry for instrument '{}' "
              "with read length '{}'. Please check the provided config "
              "file ".format(instrument_type,
                             read_length))
        sys.exit(1)

    qc_engine = QCEngine(runfolder=runfolder, handler_config=handler_config)
    qc_engine.run()
    sys.exit(qc_engine.exit_status)


if __name__ == '__main__':
    start()
