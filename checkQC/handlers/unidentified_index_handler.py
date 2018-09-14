

from checkQC.handlers.qc_handler import QCHandler, QCErrorFatal, QCErrorWarning
from checkQC.parsers.demux_summary_parser import DemuxSummaryParser
from checkQC.parsers.stats_json_parser import StatsJsonParser

class UnidentifiedIndexHandler(QCHandler):
    """
    TODO
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lanes_and_indices = {}
        self.conversion_results = None

    def validate_configuration(self):
        #TODO Needs custom validation since it does not use same keys as other handlers
        pass

    def parser(self):
        return [DemuxSummaryParser.__call__, StatsJsonParser.__call__]

    def collect(self, signal):
        if isinstance(signal, tuple):
            key, value = signal
            if key == "ConversionResults":
                self.conversion_results = value
        else:
            self.lanes_and_indices[signal["lane"]] = signal["indices"]

    def check_qc(self):
        number_of_reads_per_lane = self.number_of_reads_per_lane()
        for lane, indices in self.lanes_and_indices.items():
            print(indices)
            number_of_reads_on_lane = number_of_reads_per_lane[lane]
            for index in indices:
                if self.is_significantly_represented(index, number_of_reads_on_lane):
                    # investigate rules
                    print(index)
                    yield
                else:
                    print("NOT SIGNIFICANT!")
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

    def number_of_reads_per_lane(self):
        nbr_of_reads_per_lane = {}
        for lane_dict in self.conversion_results:
            nbr_of_reads_per_lane[int(lane_dict["LaneNumber"])] = int(lane_dict["TotalClustersPF"])
        return nbr_of_reads_per_lane

    def is_significantly_represented(self, index, nbr_of_reads_on_lane):
        return float(index['count']) / nbr_of_reads_on_lane > self.qc_config['significance_threshold']
