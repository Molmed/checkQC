
from math import pow

from qc_gate.handlers.qc_handler import QCHandler, QCErrorFatal, QCErrorWarning


class UndeterminedPercentageHandler(QCHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conversion_results = None

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

            if percentage_undetermined > 0.15:
                yield QCErrorFatal("The percentage of undetermined indexes was"
                                   " to high on lane {}, it was: {}".format(lane_nbr, percentage_undetermined))
            elif percentage_undetermined > 0.01:
                yield QCErrorWarning("The percentage of undetermined indexes was "
                                     "to high on lane {}, it was: {}".format(lane_nbr, percentage_undetermined))
            else:
                continue

