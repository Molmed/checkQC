

from checkQC.handlers.qc_handler import QCHandler, QCErrorFatal, QCErrorWarning
from checkQC.parsers.demux_summary_parser import DemuxSummaryParser


class UnidentifiedIndexHandler(QCHandler):
    """
    TODO
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lanes_and_indices = {}

    def validate_configuration(self):
        #TODO Needs custom validation since it does not use same keys as other handlers
        pass

    def parser(self):
        return DemuxSummaryParser

    def collect(self, signal):
        self.lanes_and_indices[signal["lane"]] = signal["indices"]

    def check_qc(self):

        for lane, indices in self.lanes_and_indices.items():
            print(indices)
            #yield QCErrorWarning("Foo", ordering=1, data={})
            continue

        #TODO
        #for lane_dict in self.conversion_results:
        #    lane_nbr = int(lane_dict["LaneNumber"])
        #    lane_pf = lane_dict["TotalClustersPF"]

        #    if self.error() != self.UNKNOWN and lane_pf < float(self.error())*pow(10, 6):
        #        yield QCErrorFatal("Clusters PF was to low on lane {}, "
        #                           "it was: {:.2f} M".format(lane_nbr, lane_pf/pow(10, 6)),
        #                           ordering=lane_nbr,
        #                           data={'lane': lane_nbr, 'lane_pf': lane_pf, 'threshold': self.error()})
        #    elif self.warning() != self.UNKNOWN and lane_pf < float(self.warning())*pow(10, 6):
        #        yield QCErrorWarning("Cluster PF was to low on lane {}, "
        #                             "it was: {:.2f} M".format(lane_nbr, lane_pf/pow(10, 6)),
        #                             ordering=lane_nbr,
        #                             data={'lane': lane_nbr, 'lane_pf': lane_pf, 'threshold': self.warning()})
        #    else:
        #        continue
