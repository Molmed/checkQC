from checkQC.handlers.qc_handler import QCHandler, QCErrorFatal, QCErrorWarning
from checkQC.parsers.stats_json_parser import StatsJsonParser
from math import pow


class ReadsPerSampleHandler(QCHandler):

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
            lane_nbr = int(lane_dict["LaneNumber"])
            lane_demux = lane_dict["DemuxResults"]
            nbr_of_samples = len(lane_demux)

            for sample_id_info in lane_demux:

                sample_id = sample_id_info["SampleId"]
                sample_total_reads = sample_id_info["NumberReads"] / pow(10, 6)

                if self.error() != self.UNKNOWN and sample_total_reads < (float(self.error()) / float(nbr_of_samples)):
                    yield QCErrorFatal("Number of reads for sample {} was too low on lane {}, "
                                       "it was: {:.3f} M".format(sample_id, lane_nbr, sample_total_reads),
                                       ordering=lane_nbr,
                                       data={"lane": lane_nbr, "number_of_samples": nbr_of_samples,
                                             "sample_id": sample_id, "sample_reads": sample_total_reads,
                                             "threshold": self.error()})
                elif self.warning() != self.UNKNOWN and \
                                sample_total_reads < (float(self.warning()) / float(nbr_of_samples)):
                    yield QCErrorWarning("Number of reads for sample {} was too low on lane {}, "
                                         "it was: {:.3f} M".format(sample_id, lane_nbr, sample_total_reads),
                                         ordering=lane_nbr,
                                         data={"lane": lane_nbr, "number_of_samples": nbr_of_samples,
                                               "sample_id": sample_id, "sample_reads": sample_total_reads,
                                               "threshold": self.warning()})
                else:
                    continue
