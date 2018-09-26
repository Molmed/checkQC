from checkQC.handlers.qc_handler import QCHandler, QCErrorFatal, QCErrorWarning
from checkQC.parsers.stats_json_parser import StatsJsonParser
from math import pow
from collections import defaultdict


class ReadsPerSampleHandler(QCHandler):
    """
    This handler will check that the number of reads assigned to a sample is high enough. The value specified in the
    configuration is interpreted as the number of reads demanded for a single sample, i.e. the number of reads per
    sample on a lane which has multiple samples is the threshold divided by the total number of samples on the lane.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conversion_results = None

    def parser(self):
        """
        The ReadsPerSampleHandler fetches its information from the Stats.json file

        :returns: A StatsJsonParser callable
        """
        return StatsJsonParser

    def collect(self, signal):
        key, value = signal
        if key == "ConversionResults":
            self.conversion_results = value

    def check_qc(self):

        for lane_dict in self.conversion_results:
            lane_nbr = int(lane_dict["LaneNumber"])
            lane_demux = lane_dict["DemuxResults"]
            total_reads = defaultdict(float)

            for sample_id_info in lane_demux:
                sample_name = sample_id_info["SampleName"]
                total_reads[sample_name] += sample_id_info["NumberReads"] / pow(10, 6)

            nbr_of_samples = len(total_reads.keys())
            for sample, sample_total_reads in total_reads.items():

                if self.error() != self.UNKNOWN:
                    error_threshold = float(self.error()) / float(nbr_of_samples)
                if self.warning() != self.UNKNOWN:
                    warning_threshold = float(self.warning()) / float(nbr_of_samples)

                if self.error() != self.UNKNOWN and sample_total_reads < error_threshold:
                    yield QCErrorFatal("Number of reads for sample {} was too low on lane {}, "
                                       "it was: {:.3f} M".format(sample, lane_nbr, sample_total_reads),
                                       ordering=lane_nbr,
                                       data={"lane": lane_nbr, "number_of_samples": nbr_of_samples,
                                             "sample_name": sample, "sample_reads": sample_total_reads,
                                             "threshold": error_threshold})
                elif self.warning() != self.UNKNOWN and \
                                sample_total_reads < warning_threshold:
                    yield QCErrorWarning("Number of reads for sample {} was too low on lane {}, "
                                         "it was: {:.3f} M".format(sample, lane_nbr, sample_total_reads),
                                         ordering=lane_nbr,
                                         data={"lane": lane_nbr, "number_of_samples": nbr_of_samples,
                                               "sample_name": sample, "sample_reads": sample_total_reads,
                                               "threshold": warning_threshold})
                else:
                    continue
