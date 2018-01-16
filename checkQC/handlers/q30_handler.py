
from checkQC.handlers.qc_handler import QCHandler, QCErrorFatal, QCErrorWarning
from checkQC.parsers.interop_parser import InteropParser


class Q30Handler(QCHandler):
    """
    This handler checks that the percent of bases on a lane and reads with Q30 or high was
    above the specified threshold.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_results = []

    def parser(self):
        """
        The Q30Handler fetches its data from the Interop files

        :returns: A InteropParser callable
        """
        return InteropParser

    def collect(self, signal):
        key, value = signal
        if key == "percent_q30":
            self.error_results.append(value)

    def check_qc(self):

        for error_dict in self.error_results:
            lane_nbr = int(error_dict["lane"])
            read = error_dict["read"]
            percent_q30 = error_dict["percent_q30"]

            if self.error() != self.UNKNOWN and percent_q30 < self.error():
                yield QCErrorFatal("%Q30 {:.2f} was too low on lane: {} for read: {}".format(percent_q30,
                                                                                             lane_nbr,
                                                                                             read),
                                   ordering=lane_nbr,
                                   data={"lane": lane_nbr, "read": read,
                                         "percent_q30": percent_q30, "threshold": self.error()})
            elif self.warning() != self.UNKNOWN and percent_q30 < self.warning():
                yield QCErrorWarning("%Q30 {:.2f} was too low on lane: {} for read: {}".format(percent_q30,
                                                                                               lane_nbr,
                                                                                               read),
                                     ordering=lane_nbr,
                                     data={"lane": lane_nbr, "read": read,
                                           "percent_q30": percent_q30, "threshold": self.warning()})
            else:
                continue

