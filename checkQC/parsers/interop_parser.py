
from checkQC.parsers.parser import Parser

from interop import py_interop_run_metrics, py_interop_run, py_interop_summary


class InteropParser(Parser):
    """
    This Parser will get data from the Illumina Interop binary files, and send it to its subscribers as a
    tuple with the first element being the name of the element and the second one being a the actual data.

    At this point the following data which is fetched from the Interop files and is sent in the following format:

        - ("error_rate", {"lane": <lane nbr>, "read": <read nbr>, "error_rate": <error rate>}))
        - ("percent_q30", {"lane": <lane nbr>, "read": <read nbr>, "percent_q30": <percent q30>}))

    """

    def __init__(self, runfolder, parser_configurations, *args, **kwargs):
        """
        Create a InteropParser instance for the specified runfolder

        :param runfolder: to create InteropParser instance for
        :param parser_configurations: dict containing any extra configuration required by
        the parser under class name key
        """
        super().__init__(*args, **kwargs)
        self.runfolder = runfolder

    @staticmethod
    def get_non_index_reads(summary):
        """
        Pick-out the reads which are not index reads

        :param summary: a Interop read summary object to parse the read numbers from
        :returns: all reads which are not index reads
        """
        non_index_reads = []
        for read_nbr in range(summary.size()):
            if not summary.at(read_nbr).read().is_index():
                non_index_reads.append(read_nbr)
        return non_index_reads

    def run(self):
        run_metrics = py_interop_run_metrics.run_metrics()
        run_metrics.run_info()

        valid_to_load = py_interop_run.uchar_vector(py_interop_run.MetricCount, 0)
        py_interop_run_metrics.list_summary_metrics_to_load(valid_to_load)
        run_metrics.read(self.runfolder, valid_to_load)

        summary = py_interop_summary.run_summary()
        py_interop_summary.summarize_run_metrics(run_metrics, summary)

        lanes = summary.lane_count()
        reads = self.get_non_index_reads(summary)
        for lane in range(lanes):
            # The interop library uses zero based indexing, however most people uses read 1/2
            # to denote the different reads, this enumeration is used to transform from
            # zero based indexing to this form. /JD 2017-10-27
            for new_read_nbr, original_read_nbr in enumerate(reads):
                read = summary.at(original_read_nbr).at(lane)
                error_rate = read.error_rate().mean()
                percent_q30 = read.percent_gt_q30()
                percent_phix_aligned = read.percent_aligned().mean()
                self._send_to_subscribers(("error_rate",
                                           {"lane": lane+1, "read": new_read_nbr+1, "error_rate": error_rate}))
                self._send_to_subscribers(("percent_q30",
                                           {"lane": lane+1, "read": new_read_nbr+1, "percent_q30": percent_q30}))
                self._send_to_subscribers(("percent_phix",
                                           {"lane": lane+1, "read": new_read_nbr+1, "percent_phix": percent_phix_aligned}))

    def __eq__(self, other):
        if isinstance(other, self.__class__) and self.runfolder == other.runfolder:
            return True
        else:
            return False

    def __hash__(self):
        return hash(self.__class__.__name__ + self.runfolder)
