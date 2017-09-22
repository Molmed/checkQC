
import sys

import click

from checkQC.qc_engine import QCEngine
from checkQC.config import ConfigFactory
from checkQC.run_type_recognizer import RunTypeRecognizer

import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(levelname)s %(message)s')

console_log_handler = logging.StreamHandler()
logging.getLogger("").addHandler(console_log_handler)


@click.command("checkqc")
@click.option("--config_file", help="Path to the checkQC configuration file", type=click.Path())
@click.argument('runfolder', type=click.Path())
def start(config_file, runfolder):
    """
    checkQC is a command line utility designed to quickly gather and assess quality control metrics from a
    Illumina sequencing run. It is highly customizable and which quality controls modules should be run
    for a particular run type should be specified in the provided configuration file.
    """
    # -----------------------------------
    # This is the application entry point
    # -----------------------------------

    app = App(runfolder, config_file)
    app.run()
    sys.exit(app.exit_status)


class App(object):

    def __init__(self, runfolder, config_file=None):
        self._runfolder = runfolder
        self._config_file = config_file
        self.exit_status = 0

    def run(self):
        config = ConfigFactory.from_config_path(self._config_file)
        run_type_recognizer = RunTypeRecognizer(config=config, runfolder=self._runfolder)
        instrument_and_reagent_version = run_type_recognizer.instrument_and_reagent_version()

        # TODO For now assume symmetric read lengths
        read_length = int(run_type_recognizer.read_length().split("-")[0])
        handler_config = config.get_handler_config(instrument_and_reagent_version, read_length)
        qc_engine = QCEngine(runfolder=self._runfolder, handler_config=handler_config)
        qc_engine.run()
        self.exit_status = qc_engine.exit_status

if __name__ == '__main__':
    start()
