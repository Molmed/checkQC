
import yaml
import sys

from checkQC.qc_engine import QCEngine


def start():

    with open("config/config.yaml") as stream:
        config = yaml.load(stream)

    machine_type = "hiseq2500_rapid"
    read_length = '100-120'
    run_mode = "paired_end"

    handler_config = config[machine_type][read_length][run_mode]["handlers"]

    runfolder = "./tests/resources/150418_SN7001335_0149_AH32CYBCXX"

    qc_engine = QCEngine(runfolder=runfolder, handler_config=handler_config)
    qc_engine.run()
    sys.exit(qc_engine.exit_status)


if __name__ == '__main__':
    start()
