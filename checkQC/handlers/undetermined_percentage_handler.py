
from checkQC.handlers.qc_handler import QCHandler, QCErrorFatal, QCErrorWarning
from checkQC.parsers.stats_json_parser import StatsJsonParser


class UndeterminedPercentageHandler(QCHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conversion_results = None

    def parser(self):
        return StatsJsonParser

    def collect(self, signal):
        key, value = signal
        if key == "ConversionResults":
            self.conversion_results = value

    def check_qc(self):

        for lane_dict in self.conversion_results:
            lane_nbr = lane_dict["LaneNumber"]
            total_yield = lane_dict["Yield"]

            undetermined_yield = lane_dict["Undetermined"]["Yield"]

            percentage_undetermined = undetermined_yield / total_yield

            if self.error() != self.UNKNOWN and percentage_undetermined > self.error():
                yield QCErrorFatal("The percentage of undetermined indexes was"
                                   " to high on lane {}, it was: {}".format(lane_nbr, percentage_undetermined),
                                   ordering=int(lane_nbr))
            elif self.warning() != self.UNKNOWN and percentage_undetermined > self.warning():
                yield QCErrorWarning("The percentage of undetermined indexes was "
                                     "to high on lane {}, it was: {}".format(lane_nbr, percentage_undetermined),
                                     ordering=int(lane_nbr))
            else:
                continue

