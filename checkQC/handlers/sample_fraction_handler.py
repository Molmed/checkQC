from checkQC.handlers.qc_handler import QCHandler, QCErrorFatal, QCErrorWarning
from checkQC.parsers.stats_json_parser import StatsJsonParser
from math import pow

class SampleFractionHandler(QCHandler):

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
            lane_demux = lane_dict["DemuxResults"]

            for sample_id_info in lane_demux:

                sample_id = sample_id_info["SampleId"]
                sample_total_reads = sample_id_info["NumberReads"] / pow(10,6)

                if self.error() != self.UNKNOWN and sample_total_reads <= (float(self.error()) / float(len(lane_demux))):
                    yield QCErrorFatal("Sample fraction for sample {} was to low on lane {}, it was: {}".format(sample_id, lane_nbr, sample_total_reads),
                                       ordering=int(lane_nbr))
                elif self.warning() != self.UNKNOWN and sample_total_reads <= (float(self.warning()) / float(len(lane_demux))):
                    yield QCErrorWarning("Sample fraction for sample {} was to low on lane {}, it was: {}".format(sample_id, lane_nbr, sample_total_reads),
                                         ordering=int(lane_nbr))
                else:
                    continue
