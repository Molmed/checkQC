from math import pow

from checkQC.handlers.qc_handler import QCHandler, QCErrorFatal, QCErrorWarning
from checkQC.parsers.stats_json_parser import StatsJsonParser


class ClusterPFHandler(QCHandler):
    """
    This handler will check that the number of clusters passing filter on a lane passes the set criteria.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conversion_results = None

    def parser(self):
        """
        The ClusterPFHandler will gather its data from the Stats.json file

        :returns: a StatsJsonParser callable
        """
        return StatsJsonParser

    def collect(self, signal):
        key, value = signal
        if key == "ConversionResults":
            self.conversion_results = value

    def check_qc(self):
        for lane_dict in self.conversion_results:
            lane_nbr = int(lane_dict["LaneNumber"])
            lane_pf = lane_dict["TotalClustersPF"]

            if self.error() != self.UNKNOWN and lane_pf < float(self.error())*pow(10, 6):
                yield QCErrorFatal("Clusters PF was to low on lane {}, "
                                   "it was: {:.2f} M".format(lane_nbr, lane_pf/pow(10, 6)),
                                   ordering=lane_nbr,
                                   data={'lane': lane_nbr, 'lane_pf': lane_pf, 'threshold': self.error()})
            elif self.warning() != self.UNKNOWN and lane_pf < float(self.warning())*pow(10, 6):
                yield QCErrorWarning("Cluster PF was to low on lane {}, "
                                     "it was: {:.2f} M".format(lane_nbr, lane_pf/pow(10, 6)),
                                     ordering=lane_nbr,
                                     data={'lane': lane_nbr, 'lane_pf': lane_pf, 'threshold': self.warning()})
            else:
                continue
