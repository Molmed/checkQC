import interop
import csv
import pathlib

from checkQC.handlers.qc_handler import QCErrorFatal, QCErrorWarning

from checkQC.qc_checkers.utils import handler2checker

class QCData:
    def __init__(
        self,
        instrument,
        read_length,
        samplesheet,
        sequencing_metrics,  # TODO validate dict content
        # The schema will define mandatory fields but may evolve over time with
        # new instruments
    ):
        self.instrument = instrument
        self.read_length = read_length
        self.samplesheet = samplesheet
        self.sequencing_metrics = sequencing_metrics

    from checkQC.parsers.illumina import from_bclconvert

    from checkQC.qc_checkers import error_rate, reads_per_sample

    from checkQC.views.illumina import illumina_view

    def report(self, config):
        # TODO select correct config based on read_len and instrument
        # TODO make sure default_handlers are included
        # TODO add optional parameter to select closest read length
        # TODO validate config with schema
        #   - schema could be dynamic, i.e. we add the handlers named allowed
        #   based on the methods defined in QCData

        qc_reports = [
            qc_report
            for handler_config in config["handlers"]
            for qc_report in getattr(
                self, handler2checker(handler_config["name"]))(**handler_config)
        ]

        return getattr(self, config.get("view", "illumina_view"))(qc_reports)
