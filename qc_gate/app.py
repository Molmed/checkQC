
from qc_gate.parsers.stats_json_parser import StatsJsonParser
from qc_gate.handlers.yield_handler import YieldHandler
from qc_gate.handlers.undetermined_percentage_handler import UndeterminedPercentageHandler


def start():

    parser = StatsJsonParser("Stats.json")

    s1 = YieldHandler()
    s2 = UndeterminedPercentageHandler()
    subscribers = [s1, s2]

    parser.add_subscribers(subscribers)
    parser.run()

    for subscriber in subscribers:
        subscriber.report()


if __name__ == '__main__':
    start()