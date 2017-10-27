
from checkQC.handlers.qc_handler import QCHandler, QCErrorFatal, QCErrorWarning
from checkQC.parsers.interop_parser import InteropParser


class Q30Handler(QCHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_results = []

    def parser(self):
        return InteropParser

    def collect(self, signal):
        key, value = signal
        if key == "percent_q30":
            self.error_results.append(value)

    def check_qc(self):

        for error_dict in self.error_results:
            lane_nbr = error_dict["lane"]
            read = error_dict["read"]
            percent_q30 = error_dict["percent_q30"]

            if self.error() != self.UNKNOWN and percent_q30 < self.error():
                yield QCErrorFatal("%Q30 {:.2f} was too low on lane: {} for read: {}".format(percent_q30,
                                                                                             lane_nbr,
                                                                                             read),
                                   ordering=int(lane_nbr))
            elif self.warning() != self.UNKNOWN and percent_q30 < self.warning():
                yield QCErrorWarning("%Q30 {:.2f} was too low on lane: {} for read: {}".format(percent_q30,
                                                                                               lane_nbr,
                                                                                               read),
                                     ordering=int(lane_nbr))
            else:
                continue

