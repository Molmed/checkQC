
import yaml

from qc_gate.parsers.stats_json_parser import StatsJsonParser
from qc_gate.handlers.qc_handler import QCHandler


def start():

    with open("config/config.yaml") as stream:
        config = yaml.load(stream)

    machine_type = "hiseq2500_rapid"
    read_length = '100-120'
    run_mode = "paired_end"

    handler_list = config[machine_type][read_length][run_mode]["handlers"]

    subscribers = []

    for clazz_config in handler_list:
        subscribers.append(QCHandler.create_subclass_instance(clazz_config["name"]))

    parser = StatsJsonParser("Stats.json")
    parser.add_subscribers(subscribers)
    parser.run()

    for subscriber in subscribers:
        subscriber.report()


if __name__ == '__main__':
    start()