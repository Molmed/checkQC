
import yaml

from qc_gate.parsers.stats_json_parser import StatsJsonParser
from qc_gate.handlers.qc_handler import QCHandler
from qc_gate.qc_engine import QCEngine


def start():

    with open("config/config.yaml") as stream:
        config = yaml.load(stream)

    machine_type = "hiseq2500_rapid"
    read_length = '100-120'
    run_mode = "paired_end"

    handler_list = config[machine_type][read_length][run_mode]["handlers"]

    qc_engine = QCEngine(runfolder='.')
    qc_engine.create_handlers(handler_list, runfolder='.')
    qc_engine.initiate_parsers()
    qc_engine.run()
    qc_engine.compile_reports()


    #parser = StatsJsonParser("Stats.json")
    #parser.add_subscribers(subscribers)
    #parser.run()

    #for subscriber in subscribers:
    #    subscriber.report()


if __name__ == '__main__':
    start()