
import sys

from checkQC.qc_engine import QCEngine
from checkQC.config import get_config
from checkQC.run_type_recognizer import RunTypeRecognizer


def start():

    config = get_config("config/config.yaml")

    runfolder = "./tests/resources/MiSeqDemo"

    run_type_recognizer = RunTypeRecognizer(config=config, runfolder=runfolder)
    instrument_type = run_type_recognizer.instrument_type()
    run_mode = run_type_recognizer.single_or_paired_end()
    read_length = run_type_recognizer.read_length()

    handler_config = config[instrument_type][read_length][run_mode]["handlers"]

    qc_engine = QCEngine(runfolder=runfolder, handler_config=handler_config)
    qc_engine.run()
    sys.exit(qc_engine.exit_status)


if __name__ == '__main__':
    start()
