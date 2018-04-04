
from checkQC.handlers.qc_handler import QCHandler, QCErrorFatal, QCErrorWarning
from checkQC.parsers.stats_json_parser import StatsJsonParser


class UndeterminedPercentageHandler(QCHandler):
    """
    This handler will check that the percentage of undetermined reads on a lane is below the specified threshold.
    If there are no indexes specified for the lane, this will be skipped.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conversion_results = None

    def parser(self):
        """
        The UndeterminedPercentageHandler fetches its data from the Stats.json file

        :returns: A StatsJsonParser callable
        """
        return StatsJsonParser

    def collect(self, signal):
        key, value = signal
        if key == "ConversionResults":
            self.conversion_results = value

    def check_qc(self):

        for lane_dict in self.conversion_results:
            # If no index was specified for a lane, there will be no
            # Undetermined key for that lane in the Stats.json file. /JD 2017-10-02
            if lane_dict.get("Undetermined"):
                lane_nbr = int(lane_dict["LaneNumber"])
                total_yield = lane_dict["Yield"]

                if total_yield == 0:
                    yield QCErrorFatal("Yield for lane: {} was 0. No undetermined percentage could be computed.",
                                       ordering=lane_nbr,
                                       data={"lane": lane_nbr, "percentage_undetermined": "N/A"})
                    continue

                undetermined_yield = lane_dict["Undetermined"]["Yield"]

                percentage_undetermined = (undetermined_yield / total_yield)*100

                if self.error() != self.UNKNOWN and percentage_undetermined > self.error():
                    yield QCErrorFatal("The percentage of undetermined indexes was"
                                       " to high on lane {}, it was: {:.2f}%".format(lane_nbr, percentage_undetermined),
                                       ordering=lane_nbr,
                                       data={"lane": lane_nbr, "percentage_undetermined": percentage_undetermined,
                                             "threshold": self.error()})
                elif self.warning() != self.UNKNOWN and percentage_undetermined > self.warning():
                    yield QCErrorWarning("The percentage of undetermined indexes was "
                                         "to high on lane {}, it was: {:.2f}%".format(lane_nbr, percentage_undetermined),
                                         ordering=lane_nbr,
                                         data={"lane": lane_nbr, "percentage_undetermined": percentage_undetermined,
                                               "threshold": self.warning()})
                else:
                    continue

