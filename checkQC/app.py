
import sys
import json
import logging

import click

from checkQC.qc_engine import QCEngine
from checkQC.config import ConfigFactory
from checkQC.run_type_recognizer import RunTypeRecognizer
from checkQC import __version__ as checkqc_version


logging.basicConfig(level=logging.DEBUG,
                    format='%(levelname)-8s %(message)s')

console_log_handler = logging.StreamHandler()
log = logging.getLogger("")


@click.command("checkqc")
@click.option("--config", help="Path to the checkQC configuration file", type=click.Path())
@click.option('--json', is_flag=True, default=False, help="Print the results of the run as json to stdout")
@click.option('--version', is_flag=True, default=False, help="Print the version of checkQC to stdout")
@click.argument('runfolder', type=click.Path())
def start(config, json, version, runfolder):
    """
    checkQC is a command line utility designed to quickly gather and assess quality control metrics from an
    Illumina sequencing run. It is highly customizable and which quality controls modules should be run
    for a particular run type should be specified in the provided configuration file.
    """
    # -----------------------------------
    # This is the application entry point
    # -----------------------------------

    if version:
        print(checkqc_version)
    else:
        app = App(runfolder, config, json)
        app.run()
        sys.exit(app.exit_status)


class App(object):

    def __init__(self, runfolder, config_file=None, json_mode=False):
        self._runfolder = runfolder
        self._config_file = config_file
        self._json_mode = json_mode
        self.exit_status = 0

    def configure_and_run(self):
        config = ConfigFactory.from_config_path(self._config_file)
        run_type_recognizer = RunTypeRecognizer(config=config, runfolder=self._runfolder)
        instrument_and_reagent_version = run_type_recognizer.instrument_and_reagent_version()

        # TODO For now assume symmetric read lengths
        read_length = int(run_type_recognizer.read_length().split("-")[0])
        handler_config = config.get_handler_config(instrument_and_reagent_version, read_length)
        qc_engine = QCEngine(runfolder=self._runfolder, handler_config=handler_config)
        reports = qc_engine.run()
        self.exit_status = qc_engine.exit_status
        return reports

    def run(self):
        log.info("------------------------")
        log.info("Starting checkQC ({})".format(checkqc_version))
        log.info("------------------------")
        log.info("Runfolder is: {}".format(self._runfolder))
        reports = self.configure_and_run()
        if self.exit_status == 0:
            log.info("Finished without finding any fatal qc errors.")
        else:
            log.info("Finished with fatal qc errors and will exit with non-zero exit status.")

        if self._json_mode:
            print(json.dumps(reports))

if __name__ == '__main__':
    start()
