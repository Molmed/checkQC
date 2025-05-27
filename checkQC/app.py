import sys
import json
import logging
from pathlib import Path
import warnings

import click

from checkQC.qc_engine import QCEngine
from checkQC.config import ConfigFactory
from checkQC.run_type_recognizer import RunTypeRecognizer
from checkQC.run_type_summarizer import RunTypeSummarizer
from checkQC.exceptions import CheckQCException, RunfolderNotFoundError
from checkQC import __version__ as checkqc_version
from checkQC.qc_data import QCData
from checkQC.qc_reporter import QCReporter


SUPPORTED_DEMUXERS = [
    "bcl2fastq",
    "bclconvert",
]


warnings.simplefilter("default")
logging.basicConfig(level=logging.INFO,
                    format='%(levelname)-8s %(message)s')

console_log_handler = logging.StreamHandler()
log = logging.getLogger(__name__)


@click.command("checkqc")
@click.option(
    "--config",
    type=click.Path(exists=True, dir_okay=False),
    help="Path to the checkQC configuration file",
)
@click.option(
    "--json", "json_mode",
    is_flag=True, default=False,
    help="Print the results of the run as json to stdout",
)
@click.option(
    "--downgrade-errors",
    type=str, multiple=True,
    help="Downgrade errors to warnings for a specific handler, can be used multiple times",
)
@click.option(
    "--use-closest-read-length",
    is_flag=True, default=False,
    help="Use the closest read length if the read length used isn't specified in the config",
)
@click.option(
    "--demultiplexer",
    type=click.Choice(
        SUPPORTED_DEMUXERS,
        case_sensitive=False,
    ),
    default="bcl2fastq",
    help="Specify which demultiplexer was used to generate the data",
)
@click.version_option(checkqc_version)
@click.argument(
    "runfolder",
    type=click.Path(exists=True, file_okay=False),
)
def start(
    config,
    json_mode,
    downgrade_errors,
    use_closest_read_length,
    demultiplexer,
    runfolder,
):
    """
    checkQC is a command line utility designed to quickly gather and assess quality control metrics from an
    Illumina sequencing run. It is highly customizable and which quality controls modules should be run
    for a particular run type should be specified in the provided configuration file.
    """
    # -----------------------------------
    # This is the application entry point
    # -----------------------------------

    if json_mode:
        warnings.warn("`--json` is being deprecated in favor of custom views and only works when the demultiplexer is bcl2fastq.", DeprecationWarning)

    if demultiplexer == 'bcl2fastq':
        app = App(
            runfolder,
            config,
            json_mode,
            downgrade_errors,
            use_closest_read_length,
        )
        app.run()
        sys.exit(app.exit_status)
    else:
        log.info("------------------------")
        log.info(f"Starting checkQC ({checkqc_version})")
        log.info("------------------------")
        log.info(f"Runfolder is: {runfolder}")

        exit_status, reports = run_new_checkqc(
            config,
            runfolder,
            downgrade_errors,
            use_closest_read_length,
            demultiplexer,
        )

        if exit_status == 0:
            log.info("Finished without finding any fatal qc errors.")
        else:
            log.info("Finished with fatal qc errors and will exit with non-zero exit status.")

        print(reports)

        sys.exit(exit_status)


def run_new_checkqc(
    config,
    runfolder_path,
    downgrade_errors_for,
    use_closest_read_length,
    demultiplexer,
):
    runfolder_path = Path(runfolder_path)
    assert runfolder_path.is_dir()

    config = ConfigFactory.from_config_path(config)._config

    qc_data_constructor = getattr(QCData, f"from_{demultiplexer}")
    qc_data = qc_data_constructor(
        runfolder_path=runfolder_path,
        parser_config=(
            config
            .get("parser_configurations", {})
            .get(f"from_{demultiplexer}", {})
        ),
    )

    qc_reporter = QCReporter(config)

    exit_status, reports = qc_reporter.gather_reports(
        qc_data,
        use_closest_read_len=use_closest_read_length,
        downgrade_errors_for=downgrade_errors_for,
    )

    return exit_status, reports


class App(object):
    """
    This is the main application object for CheckQC.
    """

    def __init__(
        self,
        runfolder,
        config_file=None,
        json_mode=False,
        downgrade_errors_for=(),
        use_closest_read_length=False,
    ):
        self._runfolder = runfolder
        self._config_file = config_file
        self._json_mode = json_mode
        self._downgrade_errors_for = downgrade_errors_for
        self._use_closest_read_length = use_closest_read_length
        self.exit_status = 0

    def configure_and_run(self):
        """
        Configures and runs the application. It will set the exit status of the object in accordance with if any
        fatal qc errors were found or not.

        :returns: The reports of the application as a dict
        """
        config = ConfigFactory.from_config_path(self._config_file)
        parser_configurations = config.get("parser_configurations", None)

        if not Path(self._runfolder).is_dir():
            raise RunfolderNotFoundError("Could not find runfolder: {}. Are you "
                                         "sure the path is correct?".format(self._runfolder))

        run_type_recognizer = RunTypeRecognizer(runfolder=self._runfolder)
        instrument_and_reagent_version = run_type_recognizer.instrument_and_reagent_version()

        # TODO For now assume symmetric read lengths
        both_read_lengths = run_type_recognizer.read_length()
        read_length = int(both_read_lengths.split("-")[0])
        handler_config = config.get_handler_configs(instrument_and_reagent_version, read_length,
                                                    self._downgrade_errors_for, self._use_closest_read_length)

        run_type_summary = RunTypeSummarizer.summarize(instrument_and_reagent_version, both_read_lengths, handler_config)

        qc_engine = QCEngine(runfolder=self._runfolder,
                             parser_configurations=parser_configurations,
                             handler_config=handler_config)
        reports = qc_engine.run()
        reports["run_summary"] = run_type_summary
        self.exit_status = qc_engine.exit_status
        return reports

    def run(self):
        """
        This method will run CheckQC as it is intended to run as a commandline application, it will log to the
        stderr and write data to stdout.

        :returns: the exit status of the run (0 for success, else not 0)
        """
        log.info("------------------------")
        log.info("Starting checkQC ({})".format(checkqc_version))
        log.info("------------------------")
        log.info("Runfolder is: {}".format(self._runfolder))
        try:
            reports = self.configure_and_run()
            if self.exit_status == 0:
                log.info("Finished without finding any fatal qc errors.")
            else:
                log.error("Finished with fatal qc errors and will exit with non-zero exit status.")

            if self._json_mode:
                print(json.dumps(reports))

        except CheckQCException as e:
            log.error(e)
            self.exit_status

        return self.exit_status

if __name__ == '__main__':
    start()
