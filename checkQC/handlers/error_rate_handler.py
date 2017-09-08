
from checkQC.handlers.qc_handler import QCHandler, QCErrorFatal, QCErrorWarning
from checkQC.parsers.interop_parser import InteropParser


class ErrorRateHandler(QCHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_results = []

    def parser(self):
        return InteropParser

    def collect(self, signal):
        key, value = signal
        if key == "error_rate":
            self.error_results.append(value)

    def check_qc(self):

        for error_dict in self.error_results:
            lane_nbr = error_dict["lane"]
            read = error_dict["read"]
            error_rate = error_dict["error_rate"]

            if self.error() != self.UNKNOWN and error_rate > self.error():
                yield QCErrorFatal("Error rate {} was to high on lane: {} for read: {}".format(error_rate,
                                                                                               lane_nbr,
                                                                                               read),
                                   ordering=int(lane_nbr))
            elif self.warning() != self.UNKNOWN and error_rate > self.warning():
                yield QCErrorWarning("Error rate {} was to high on lane: {} for read: {}".format(error_rate,
                                                                                                 lane_nbr,
                                                                                                 error_rate),
                                     ordering=int(lane_nbr))
            else:
                continue

