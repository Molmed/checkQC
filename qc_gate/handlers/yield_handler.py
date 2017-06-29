
from math import pow

from qc_gate.handlers.qc_handler import QCHandler, QCErrorFatal, QCErrorWarning


class YieldHandler(QCHandler):

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
            lane_yield = lane_dict["Yield"]

            if lane_yield < 200*pow(10, 8):
                yield QCErrorFatal("Yield was to low on lane {}, it was: {}".format(lane_nbr, lane_yield))
            elif lane_yield < 400*pow(10, 8):
                yield QCErrorWarning("Yield was to low on lane {}, it was: {}".format(lane_nbr, lane_yield))
            else:
                continue

