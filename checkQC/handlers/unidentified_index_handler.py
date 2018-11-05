
from collections import defaultdict

from checkQC.handlers.qc_handler import QCHandler, QCErrorWarning
from checkQC.parsers.demux_summary_parser import DemuxSummaryParser
from checkQC.parsers.stats_json_parser import StatsJsonParser
from checkQC.parsers.samplesheet_parser import SamplesheetParser
from checkQC.exceptions import ConfigurationError


class UnidentifiedIndexHandler(QCHandler):
    """
    The UnidentifiedIndexHandler will try to identify if an index is represented at to high a level in unidenfied
    reads, and if that is the case try to pinpoint why that is.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lanes_and_indices = {}
        self.conversion_results = None
        self.samplesheet = None

    def validate_configuration(self):
        """
        This overrides the normal configuration which looks for warning/error.
        :return: None
        :raises: ConfigurationError if the configuration for the handler was not valid.
        """
        try:
            float(self.qc_config['significance_threshold']) / 100
        except KeyError:
            raise ConfigurationError("The {} handler expects 'significance_threshold' to be set. "
                                     "Perhaps it is missing from the configuration "
                                     "file?".format(self.__class__.__name__))

    def parser(self):
        return [DemuxSummaryParser, StatsJsonParser, SamplesheetParser]

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
                # Unknown index means that the sample was run without an index.
                if self.is_significantly_represented(index, number_of_reads_on_lane) and not tag == 'unknown' \
                        and 'N' not in tag:
                    yield from self.evaluate_index_rules(tag, lane, samplesheet_dict)
                else:
                    continue

    def evaluate_index_rules(self, tag, lane, samplesheet_dict):
        rules = [self.always_warn_rule, self.check_swapped_dual_index, self.check_reversed_index,
                 self.check_reverse_complement_index, self.check_if_index_in_other_lane,
                 self.check_complement_index]
        for rule in rules:
            yield from rule(tag, lane, samplesheet_dict)

    def yield_qc_warning_with_message(self, msg, lane, tag):
        yield QCErrorWarning(msg=msg, ordering="{}:{}".format(lane, tag), data={'lane': lane, 'msg': msg})

    def always_warn_rule(self, tag, lane, samplesheet_dict):
        """
        We always want to warn about an index that is significantly represented. This rule
        will make sure that we do so, and all other rules will contribute extra information
        if there is any.
        :param tag:
        :param lane:
        :param samplesheet_dict:
        :return:
        """
        yield from self.yield_qc_warning_with_message("Index: {} was significantly overrepresented "
                                                      "on lane: {}".format(lane, tag),
                                                      lane,
                                                      tag)

    def check_swapped_dual_index(self, tag, lane, samplesheet_dict):
        if '+' in tag:
            split_tag = tag.split('+')
            swapped_tag = '{}+{}'.format(split_tag[1], split_tag[0])
            hits = self.index_in_samplesheet(samplesheet_dict, swapped_tag)
            for hit in hits:
                msg = '\tIt appears that maybe the dual index tag: {} was swapper. There was a hit for' \
                      ' the swapped index: {} at: {}'.format(tag, swapped_tag, hit)
                yield from self.yield_qc_warning_with_message(msg, lane, tag)

    def check_reversed_index(self, tag, lane, samplesheet_dict):
        hits = self.index_in_samplesheet(samplesheet_dict, tag[::-1])
        for hit in hits:
            msg = '\tWe found a possible match for the reverse of tag: {}, on: {}'.format(tag, hit)
            yield from self.yield_qc_warning_with_message(msg, lane, tag)

    def check_reverse_complement_index(self, tag, lane, samplesheet_dict):
        hits = self.index_in_samplesheet(samplesheet_dict, self.get_complementary_sequence(tag)[::-1])
        for hit in hits:
            msg = '\tWe found a possible match for the reverse complement of tag: {}, on: {}'.format(tag, hit)
            yield from self.yield_qc_warning_with_message(msg, lane, tag)

    def check_complement_index(self, tag, lane, samplesheet_dict):
        hits = self.index_in_samplesheet(samplesheet_dict, self.get_complementary_sequence(tag))
        for hit in hits:
            msg = '\tWe found a possible match for the complementary of tag: {}, on: {}'.format(tag, hit)
            yield from self.yield_qc_warning_with_message(msg, lane, tag)

    def check_if_index_in_other_lane(self, tag, lane, samplesheet_dict):
        hits = self.index_in_samplesheet(samplesheet_dict, tag)
        for hit in hits:
            msg = '\tWe found a possible match for the tag: {}, on another lane: {}'.format(tag, hit)
            yield from self.yield_qc_warning_with_message(msg, lane, tag)

    @staticmethod
    def transform_samplesheet_to_dict(samplesheet):
        samplesheet_dict = defaultdict(lambda: defaultdict(default_factory={}))
        for s in samplesheet:
            index = s['index']
            if s.get('index2'):
                index += '+{}'.format(s['index2'])
            # MiSeqs for example do not have lanes in their samplesheets, thus we will default to using lane 1
            # if nothing has been specified in the samplesheet. /JD 20181101
            lane = s.get('Lane', '1')
            samplesheet_dict[lane][index] = s['Sample_Name']

        return samplesheet_dict

    class SearchHit(object):
        def __init__(self, search_index, found_sample, found_lane):
            self.search_index = search_index
            self.found_sample = found_sample
            self.found_lane = found_lane

        def __str__(self):
            return "Lane: {}, for sample: {}. The tag we found was: {}".format(self.found_lane,
                                                                               self.found_sample,
                                                                               self.search_index)

    def index_in_samplesheet(self, samplesheet_dict, index):
        for lane, indicies in samplesheet_dict.items():
            for i in indicies:
                if index == i:
                    yield self.SearchHit(i, samplesheet_dict[lane][i], lane)

    def number_of_reads_per_lane(self):
        nbr_of_reads_per_lane = {}
        for lane_dict in self.conversion_results:
            nbr_of_reads_per_lane[int(lane_dict["LaneNumber"])] = int(lane_dict["TotalClustersPF"])
        return nbr_of_reads_per_lane

    def is_significantly_represented(self, index, nbr_of_reads_on_lane):
        #TODO Should perhaps be dynamic to number of samples on lane.
        #     Haven't really figured out how that would work just yet though.
        #     /JD 2018-09-21
        return float(index['count']) / nbr_of_reads_on_lane > self.qc_config['significance_threshold']

    def get_complementary_sequence(self, seq):
        conv_table = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G', 'N': 'N', '+': '+'}
        comp_seq = ''
        for c in seq:
            comp_seq += conv_table[c]
        return comp_seq

