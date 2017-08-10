
import sys

import click

from checkQC.qc_engine import QCEngine
from checkQC.config import get_config, get_handler_config
from checkQC.run_type_recognizer import RunTypeRecognizer


@click.command("checkQC")
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

    app = App(config_file, runfolder)
    app.run()
    sys.exit(app.exit_status)


class App(object):

    def __init__(self, runfolder, config_file=None):
        self._runfolder = runfolder
        self._config_file = config_file
        self.exit_status = 0

    def run(self):
        try:
            config = get_config(self._config_file)

            run_type_recognizer = RunTypeRecognizer(config=config, runfolder=self._runfolder)
            instrument_type = run_type_recognizer.instrument_type()
            reagent_version = run_type_recognizer.reagent_version()

            # TODO For now assume symmetric read lengths
            read_length = int(run_type_recognizer.read_length().split("-")[0])

            instrument_and_reagent_type = "_".join([instrument_type, reagent_version])

            handler_config = get_handler_config(config, instrument_and_reagent_type, read_length)
            qc_engine = QCEngine(runfolder=self._runfolder, handler_config=handler_config)
            qc_engine.run()
            self.exit_status = qc_engine.exit_status

        except Exception as e:
            print("Got an exception when running checkQC: {}".format(e))
            self.exit_status = 1

if __name__ == '__main__':
    start()
