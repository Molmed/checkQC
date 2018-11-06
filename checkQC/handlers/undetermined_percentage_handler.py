
from collections import defaultdict

from checkQC.handlers.qc_handler import QCHandler, QCErrorFatal, QCErrorWarning
from checkQC.parsers.stats_json_parser import StatsJsonParser
from checkQC.parsers.interop_parser import InteropParser


class UndeterminedPercentageHandler(QCHandler):
    """
    This handler will check that the percentage of undetermined reads on a lane is below the specified threshold.
    If there are no indexes specified for the lane, this will be skipped.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conversion_results = None
        self.phix_aligned = defaultdict(dict)

    def parser(self):
        """
        The UndeterminedPercentageHandler fetches its data from the Stats.json file

        :returns: A list of a StatsJsonParser callable and a InteropParser
        """
        return [StatsJsonParser, InteropParser]

    def collect(self, signal):
        key, value = signal
        if key == "ConversionResults":
            self.conversion_results = value
        if key == "percent_phix":
            self.phix_aligned[value["lane"]][value["read"]] = value["percent_phix"]

    def _compute_mean_percentage_phix_aligned_for_lanes(self):
        lane_and_mean_percentage_phix_aliged = {}
        for lane, reads in self.phix_aligned.items():
            mean = 0
            for read, value in reads.items():
                mean += value / len(reads)
            lane_and_mean_percentage_phix_aliged[lane] = mean
        return lane_and_mean_percentage_phix_aliged

    def check_qc(self):

        mean_phix_per_lane = self._compute_mean_percentage_phix_aligned_for_lanes()

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

                def compute_threshold(value):
                    return value + mean_phix_per_lane[lane_nbr]

                def create_data_dict(value):
                    return {"lane": lane_nbr,
                            "percentage_undetermined": percentage_undetermined,
                            "threshold": value,
                            "computed_threshold": compute_threshold(value),
                            "phix_on_lane": mean_phix_per_lane[lane_nbr]}

                if self.error() != self.UNKNOWN and percentage_undetermined > compute_threshold(self.error()):
                    yield QCErrorFatal("The percentage of undetermined indexes was"
                                       " to high on lane {}, it was: {:.2f}%".format(lane_nbr,
                                                                                     percentage_undetermined),
                                       ordering=lane_nbr,
                                       data=create_data_dict(self.error()))
                elif self.warning() != self.UNKNOWN and percentage_undetermined > compute_threshold(self.warning()):
                    yield QCErrorWarning("The percentage of undetermined indexes was "
                                         "to high on lane {}, it was: {:.2f}%".format(lane_nbr,
                                                                                      percentage_undetermined),
                                         ordering=lane_nbr,
                                         data=create_data_dict(self.warning()))
                else:
                    continue

