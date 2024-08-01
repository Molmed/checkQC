
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

    At this point the following data is fetched from the 
    Interop files and sent in the following format:

        - ("error_rate", {"lane": <lane nbr>,
                          "read": <read nbr>, 
                          "error_rate": <error rate>})

        - ("percent_q30", {"lane": <lane nbr>, 
                           "read": <read nbr>, 
                           "percent_q30": <percent q30>})

        - ("percent_q30_per_cycle", {"lane": <lane nbr>, 
                                          "read": <read nbr>, 
                                          "percent_q30_per_cycle": 
                                          {1: <q30 cycle 1>,
                                           2: <q30 cycle 2>,
                                           ...,
                                           n: <q30 cycle n>}})

    """

    def __init__(self, 
                 runfolder, 
                 parser_configurations, 
                 *args, 
                 **kwargs):
        """
        Create a InteropParser instance for the specified runfolder

        :param runfolder: to create InteropParser instance for
        :param parser_configurations: dict containing any extra 
        configuration required by the parser under class name key
        """
        super().__init__(*args, **kwargs)
        self.runfolder = runfolder

    @staticmethod
    def get_non_index_reads(summary):
        """
        Pick-out the reads which are not index reads

        :param summary: a Interop read summary object to parse 
        the read numbers from.
        :returns: all reads which are not index reads
        """
        non_index_reads = []
        for read_nbr in range(summary.size()):
            if not summary.at(read_nbr).read().is_index():
                non_index_reads.append(read_nbr)
        return non_index_reads
    
    @staticmethod
    def get_percent_q30_per_cycle(q_metrics, 
                                  lane_nr, 
                                  read_nr, 
                                  is_index_read):
        """
        For each lane and read get the mean percent_q30 over swath and tile
        for each cycle. The first 90% of the ccycles in a read will 
        initially be included to correct for known biases in the end 
        of the read, i.e. for a run with 151 cycles, only use the first 
        136 cycles. Also the first 5 cycles of a read will be removed since 
        there might be a quality drop there. Lane and read number are given as
        input and should be 0-indexed, i.e lane_nr should be an integer 0-7
        and read_nr should be an integer 0-3. The function will return a 
        dictionary where each key:value pair corresponds to the cycle 
        nr within the read and the mean '%>= Q30' for all tiles
        for that given cycle, read and lane.
        E.g. {6: 98.76343, 7: 98.718155, 8: 98.529205, ...,136: 98.43606}
        Note that "cycle" is selected based on the actual value in 
        'Cycle Within Read', which starts at 1, and not the position 
        in the data frame, which is 0-indexed. 
        #TODO: Investigate if the quality drop in the beginning of a read
        is instrument specific. 
        :param q_metrics: A rectangular array containing values of the 
        following 'Lane', 'Tile', 'Cycle', 'Read', 'Cycle Within Read', 
        '%>= Q20', '%>= Q30', 'Surface', 'Swath', and 'Tile Number'.
        :param lane_nr: int 
        :param read_nr: int 
        :param is_index_read: boolean 
        :returns: {int: float}
        """

        q30_cycle_df = pd.DataFrame(q_metrics)
        q30_lane_read = q30_cycle_df[
                (q30_cycle_df["Lane"] == lane_nr+1) &\
                (q30_cycle_df["Read"] == read_nr+1)]

        if is_index_read:
            end_cycle = int(max(q30_lane_read["Cycle Within Read"]))
            start_cycle = 1
        else:
            #Remove the last 90% of all cycles since 
            #they are expected to drop in q30
            end_cycle = math.ceil(
                max(q30_lane_read["Cycle Within Read"])*0.9
            )

            #Remove first 5 cycles since they are expected
            #to have a lower q30
            start_cycle = 6


        return {
            cycle: q30_lane_read[
                (q30_lane_read["Cycle Within Read"] == cycle)
            ]["%>= Q30"].mean()
            for cycle in range(start_cycle, end_cycle+1)
        }


    def run(self):
        run_metrics = py_interop_run_metrics.run_metrics()
        run_metrics.run_info()

        valid_to_load = py_interop_run.uchar_vector(
            py_interop_run.MetricCount,
            0
        )

        py_interop_run_metrics.list_summary_metrics_to_load(
            valid_to_load
        )
        run_metrics.read(self.runfolder, valid_to_load)
        
        q_metrics = imaging(self.runfolder, valid_to_load=['Q'])

        summary = py_interop_summary.run_summary()
        py_interop_summary.summarize_run_metrics(run_metrics, summary)

        lanes = summary.lane_count()

        for lane in range(lanes):
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
                                        {"lane": lane+1, 
                                         "read": read_nbr+1, 
                                         "error_rate": error_rate}))
                self._send_to_subscribers(("percent_q30",
                                        {"lane": lane+1, 
                                         "read": read_nbr+1, 
                                         "percent_q30": percent_q30, 
                                         "is_index_read":is_index_read}))
                self._send_to_subscribers(("percent_phix",
                                        {"lane": lane+1, 
                                         "read": read_nbr+1, 
                                         "percent_phix": percent_phix_aligned}))
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
