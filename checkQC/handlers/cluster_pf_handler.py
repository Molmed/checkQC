from checkQC.handlers.qc_handler import QCHandler, QCErrorFatal, QCErrorWarning
from checkQC.parsers.stats_json_parser import StatsJsonParser

class ClusterPFHandler(QCHandler):

    def __init__(self, qc_config, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conversion_results = None
        self.qc_config = qc_config

    def parser(self):
        return StatsJsonParser
