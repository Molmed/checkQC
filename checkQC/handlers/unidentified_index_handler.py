
from collections import defaultdict

from checkQC.handlers.qc_handler import QCHandler, QCErrorFatal, QCErrorWarning
from checkQC.parsers.demux_summary_parser import DemuxSummaryParser
from checkQC.parsers.stats_json_parser import StatsJsonParser
from checkQC.parsers.samplesheet_parser import SamplesheetParser

class UnidentifiedIndexHandler(QCHandler):
    """
    TODO
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lanes_and_indices = {}
        self.conversion_results = None
        self.samplesheet = None

    def validate_configuration(self):
        #TODO Needs custom validation since it does not use same keys as other handlers
        pass

    def parser(self):
        return [DemuxSummaryParser.__call__, StatsJsonParser.__call__, SamplesheetParser.__call__]

    def collect(self, signal):
        if isinstance(signal, tuple):
            key, value = signal
            if key == "ConversionResults":
                self.conversion_results = value
            if key == "samplesheet":
                self.samplesheet = value
        else:
            self.lanes_and_indices[signal["lane"]] = signal["indices"]

    def check_qc(self):

        samplesheet_dict = self.transform_samplesheet_to_dict(self.samplesheet)

        number_of_reads_per_lane = self.number_of_reads_per_lane()
        for lane, indices in self.lanes_and_indices.items():
            number_of_reads_on_lane = number_of_reads_per_lane[lane]
            for index in indices:
                tag = index['index']
                if self.is_significantly_represented(index, number_of_reads_on_lane):
                    # investigate rules

                    # Unknown index means that the sample was run without an index.
                    if tag == 'unknown':
                        continue

                    # TODO Check for swap if dual index

                    # TODO Check reversed ATTTGT -> TGTTTA
                    if self.exists_index_on_other_lanes(samplesheet_dict, tag[::-1]):
                        yield QCErrorWarning("TODO", ordering=lane, data={})

                    # TODO Reverse complement AAAA -> TTTT
                    #                    if self.reverse_complement(index['index']):
                    #                        self.reverse_complement(index['index'])
                    if self.exists_index_on_other_lanes(samplesheet_dict, self.reverse_complement(tag)):
                        yield QCErrorWarning("TODO", ordering=lane, data={})

                    # TODO Check if index is present in other lane
                    if self.exists_index_on_other_lanes(samplesheet_dict, tag):
                        yield QCErrorWarning("TODO", ordering=lane, data={})

                else:
                    continue

    @staticmethod
    def transform_samplesheet_to_dict(samplesheet):
        samplesheet_dict = defaultdict(lambda: defaultdict(default_factory={}))
        for s in samplesheet:
            index = s['index']
            if s['index2']:
                index += '+{}'.format(s['index2'])

            lane = s['Lane']
            samplesheet_dict[lane][index] = s['Sample_Name']

        return samplesheet_dict

    class SearchHit(object):
        def __init__(self, search_index, found_sample, found_lane):
            self.search_index = search_index
            self.found_sample = found_sample
            self.found_lane = found_lane

    def exists_index_on_other_lanes(self, samplesheet_dict, index):
        for lane, indicies in samplesheet_dict.items():
            for i in indicies:
                if index == i:
                    return self.SearchHit(i, samplesheet_dict[lane][i], lane)

    def number_of_reads_per_lane(self):
        nbr_of_reads_per_lane = {}
        for lane_dict in self.conversion_results:
            nbr_of_reads_per_lane[int(lane_dict["LaneNumber"])] = int(lane_dict["TotalClustersPF"])
        return nbr_of_reads_per_lane

    def is_significantly_represented(self, index, nbr_of_reads_on_lane):
        #TODO Should perhaps be dynamic to number of samples on lane
        return float(index['count']) / nbr_of_reads_on_lane > self.qc_config['significance_threshold']

    def reverse_complement(self, seq):
        conv_table = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G', 'N': 'N', '+': '+'}
        rev_seq = ''
        for c in seq:
            rev_seq += conv_table[c]
        return rev_seq

