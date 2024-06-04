
from checkQC.parsers.parser import Parser

from interop import py_interop_run_metrics, py_interop_run, \
    py_interop_summary, imaging

import pandas as pd
import math
import numpy


class InteropParser(Parser):
    """
    This Parser will get data from the Illumina Interop binary files, 
    and send it to its subscribers as a tuple with the first element 
    being the name of the element and the second one being a the actual data.

    At this point the following data which is fetched from the 
    Interop files and is sent in the following format:

        - ("error_rate", {"lane": <lane nbr>,
                          "read": <read nbr>, 
                          "error_rate": <error rate>}))

        - ("percent_q30", {"lane": <lane nbr>, 
                           "read": <read nbr>, 
                           "percent_q30": <percent q30>}))

    WIP - ("percent_q30_per_cycle", {"lane": <lane nbr>, 
                                          "read": <read nbr>, 
                                          "percent_q30_per_cycle": 
                                          [<q30 cycle 1>,
                                          ...,
                                          <q30 cycle n>]}))

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
    
    @staticmethod
    def get_percent_q30_per_cycle(q_metrics, lane_nr, read_nr, is_index_read):
        """
        For each lane, read,swath and tile get the mean percent_q30
        for each cycle. Only include the first 90% of the cycles, i.e.
        for a run with 151 cycles, only use the first 136 cycles. 
        Also remove the first 5 cycles since there might be a quality drop there.
        #TODO: Investigate if the quality drop in the beginning of a read
        is instrument specific. 
        :param q_metrics: A rectangular array containing the following
        rec.array([(1., 1101.,   1., 1.,   1., 99.73, 98.3 , 1., 1.,  1.),
           (1., 1101.,   3., 1.,   3., 99.6 , 98.37, 1., 1.,  1.), ...,
           (1., 2119., 602., 2., 301., 38.07, 13.91, 2., 1., 19.)],
           dtype=[('Lane', '<f4'), ('Tile', '<f4'), ('Cycle', '<f4'), 
           ('Read', '<f4'), ('Cycle Within Read', '<f4'), 
           ('%>= Q20', '<f4'), ('%>= Q30', '<f4'), ('Surface', '<f4'), 
           ('Swath', '<f4'), ('Tile Number', '<f4')])
        :param lane: 0-indexed lane, integer 0-7
        :param read: 0-indexed read, integer 0-3
        :returns: A list where each element is the mean percent_q30 
        for the cycle corresponding to the position in the list, i.e
        list[0] = cycle 1
        #TODO: Return a dictionary instead of a list. Use "Cycle within read"
        as the key and mean %Q30 as the value. This is to keep track of 
        the cycle since it does no longer correspond to position in list.  
        """
        q30_cycle_df = pd.DataFrame(q_metrics)
        q30_lane_read = q30_cycle_df[
                (q30_cycle_df["Lane"] == lane_nr+1) &\
                (q30_cycle_df["Read"] == read_nr+1)]
        
        q30_per_cycle = {}
        if is_index_read:
            cycles_q_metrics = int(max(q30_lane_read["Cycle Within Read"]))
            start_cycle = cycles_q_metrics - 5
            #Remove the first 2 bases in the index read.

            #TODO: How to handle for example 6bp reads in a 8bp run?
            #The first 2 bases will have a quality of 0 in our test run.
            #Is this the case for all runs?
            #For now I will solve it by only looking at the last 6 bp.

        else:
            cycles_q_metrics = math.ceil(max(q30_lane_read["Cycle Within Read"])*0.9)
            #Remove the last 90% of all cycles since they are expected to drop in q30
            start_cycle = 6
            #Remove first 5 cycles since they are expected to have a lower q30

        for cycle in range(start_cycle,cycles_q_metrics+1):
                
            q30_cycle_mean = numpy.mean(q30_lane_read[
                (q30_lane_read["Cycle Within Read"] == cycle)]["%>= Q30"])
            q30_per_cycle[cycle] = q30_cycle_mean

        return q30_per_cycle


    def run(self):
        run_metrics = py_interop_run_metrics.run_metrics()
        run_metrics.run_info()

        valid_to_load = py_interop_run.uchar_vector(py_interop_run.MetricCount, 0)
        py_interop_run_metrics.list_summary_metrics_to_load(valid_to_load)
        run_metrics.read(self.runfolder, valid_to_load)
        
        q_metrics = imaging(self.runfolder, valid_to_load=['Q'])

        summary = py_interop_summary.run_summary()
        py_interop_summary.summarize_run_metrics(run_metrics, summary)

        lanes = summary.lane_count()

        for lane in range(lanes):
            # The interop library uses zero based indexing, however most people uses read 1/2
            # to denote the different reads, this enumeration is used to transform from
            # zero based indexing to this form. /JD 2017-10-27
            for read_nbr in range(summary.size()):
                read = summary.at(read_nbr).at(lane)
                error_rate = read.error_rate().mean()
                percent_q30 = read.percent_gt_q30()
                percent_phix_aligned = read.percent_aligned().mean()
                is_index_read = summary.at(read_nbr).read().is_index()
                percent_q30_per_cycle = self.get_percent_q30_per_cycle(
                                        q_metrics,
                                        lane,
                                        read_nbr,
                                        is_index_read)
                
                self._send_to_subscribers(("error_rate",
                                        {"lane": lane+1, "read": read_nbr+1, "error_rate": error_rate}))
                self._send_to_subscribers(("percent_q30",
                                        {"lane": lane+1, "read": read_nbr+1, "percent_q30": percent_q30, "is_index_read":is_index_read}))
                self._send_to_subscribers(("percent_phix",
                                        {"lane": lane+1, "read": read_nbr+1, "percent_phix": percent_phix_aligned}))
                self._send_to_subscribers(("percent_q30_per_cycle",
                                        {"lane": lane+1,
                                         "read": read_nbr+1, 
                                         "percent_q30_per_cycle": percent_q30_per_cycle,
                                         "is_index_read": is_index_read}))

    def __eq__(self, other):
        if isinstance(other, self.__class__) and self.runfolder == other.runfolder:
            return True
        else:
            return False

    def __hash__(self):
        return hash(self.__class__.__name__ + self.runfolder)
