
from qc_gate.parsers.simple_file_parser import SimpleFileParser
from qc_gate.handlers.qc_handlers import QCHandler


def start():

    parser = SimpleFileParser("test_file")

    s1 = QCHandler("row1")
    s2 = QCHandler("row2")
    subscribers = [s1, s2]

    parser.add_subscribers(subscribers)
    parser.run()

    for subscriber in subscribers:
        subscriber.report()


if __name__ == '__main__':
    start()