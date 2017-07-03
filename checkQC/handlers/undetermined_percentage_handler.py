
from checkQC.handlers.qc_handler import QCHandler, QCErrorFatal, QCErrorWarning
from checkQC.parsers.stats_json_parser import StatsJsonParser


class UndeterminedPercentageHandler(QCHandler):

    def __init__(self, qc_config, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conversion_results = None
        self.qc_config = qc_config

    def parser(self, runfolder):
        return StatsJsonParser(runfolder)

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

            if percentage_undetermined > self.qc_config["error"]:
                yield QCErrorFatal("The percentage of undetermined indexes was"
                                   " to high on lane {}, it was: {}".format(lane_nbr, percentage_undetermined))
            elif percentage_undetermined > self.qc_config["warning"]:
                yield QCErrorWarning("The percentage of undetermined indexes was "
                                     "to high on lane {}, it was: {}".format(lane_nbr, percentage_undetermined))
            else:
                continue

