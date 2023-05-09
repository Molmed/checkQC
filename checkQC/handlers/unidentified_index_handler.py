from collections import defaultdict
import re

from checkQC.handlers.qc_handler import QCHandler, QCErrorFatal, QCErrorWarning
from checkQC.parsers.demux_summary_parser import DemuxSummaryParser
from checkQC.parsers.stats_json_parser import StatsJsonParser
from checkQC.parsers.samplesheet_parser import SamplesheetParser
from checkQC.exceptions import ConfigurationError


class UnidentifiedIndexHandler(QCHandler):
    """
    The UnidentifiedIndexHandler will try to identify if an index is
    represented at to high a level in unidentified reads, and if that is the
    case try to pinpoint why that is.

    It will not output errors, but all information will be displayed as
    warnings, due to the difficulty of deciding what is an error or not in this
    context. For most cases the % of unidentified reads will be what is used to
    issue the error, and then the warnings from this handler can help in
    identifying the possible underlying cause.

    There are a number of different checks (or rules) in place, which will be
    checked if and index occurs more then the `significance_threshold`. The
    samplesheet will be checked to see if the index found matches and of the
    following rules:
    - Check if the dual indexes have been swapped
    - Check if the index has been reversed
    - Check if the index is the reverse complement
    - Check if the index is the complementary index
    - Check if the index is present in another lane

    It will ignore any indexes which have N's in them. These are assumed to be
    read errors.
    """

    WHITE_LIST_QC_KEY = 'white_listed_indexes'

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
            self.qc_config['significance_threshold']
        except KeyError:
            raise ConfigurationError("The {} handler expects 'significance_threshold' to be set. "
                                     "Perhaps it is missing from the configuration "
                                     "file?".format(self.__class__.__name__))

    def parser(self):
        """
        The UnidentifiedIndexHandler fetches its information from the
        :return:
        """
        return [DemuxSummaryParser, StatsJsonParser, SamplesheetParser]

    def collect(self, signal):
        key, value = signal
        if key == "ConversionResults":
            self.conversion_results = value
        if key == "samplesheet":
            self.samplesheet = value
        if key == "index_counts":
            self.lanes_and_indices[value["lane"]] = value["indices"]

    def check_qc(self):

        samplesheet_searcher = _SamplesheetSearcher(samplesheet=self.samplesheet)
        number_of_reads_per_lane = self.number_of_reads_per_lane()

        for lane, indices in self.lanes_and_indices.items():
            number_of_reads_on_lane = number_of_reads_per_lane[lane]
            for index in indices:
                tag = index['index']
                count = index['count']
                if self.should_be_evaluated(tag, count, number_of_reads_on_lane):
                    percent_on_lane = (float(count) / number_of_reads_on_lane) * 100
                    yield from self.evaluate_index_rules(tag, lane, samplesheet_searcher, percent_on_lane)
                else:
                    continue

    def should_be_evaluated(self, tag, count, number_of_reads_on_lane):
        # Unknown index means that the sample was run without an index.
        # Ns indicate errors in read
        return not tag == 'unknown' and \
               self.is_significantly_represented(count, number_of_reads_on_lane)

    def _tag_in_white_list(self, tag):
        # This preserves backward compatiblity for users that do not specify
        # the 'white_listed_indexes' in their configs. /JD 2019-06-12
        if not self.qc_config.get(self.WHITE_LIST_QC_KEY):
            return 'N' in tag
        else:
            for regex in self.qc_config[self.WHITE_LIST_QC_KEY]:
                pattern = re.compile(regex)
                if pattern.match(tag):
                    return True
            return False

    def is_significantly_represented(self, index_count, nbr_of_reads_on_lane):
        return (float(index_count) / nbr_of_reads_on_lane) > \
               (float(self.qc_config['significance_threshold']) / 100)

    def evaluate_index_rules(self, tag, lane, samplesheet_searcher, percent_on_lane):
        """
        Evaluates a list of 'rules' and yields all warnings found by these rules.
        :param tag:
        :param lane:
        :param samplesheet_searcher:
        :param percent_on_lane:
        :return: generator of QCErrorFatal
        """
        rules = [self.always_warn_rule, self.check_reversed_index,
                 self.check_reverse_complement_index, self.check_if_index_in_other_lane,
                 self.check_complement_index]
        for rule in rules:
            yield from rule(tag=tag,
                            lane=lane,
                            samplesheet_searcher=samplesheet_searcher,
                            percent_on_lane=percent_on_lane)

        dual_index_rules = [self.check_swapped_dual_index, self.check_reverse_complement_in_dual_index,
                            self.check_reversed_in_dual_index, self.check_complement_in_dual_index]

        if '+' in tag:
            for rule in dual_index_rules:
                yield from rule(tag=tag,
                                lane=lane,
                                samplesheet_searcher=samplesheet_searcher,
                                percent_on_lane=percent_on_lane)

    @staticmethod
    def yield_qc_warning_with_message(msg, lane, tag):
        yield QCErrorFatal(msg=msg, ordering="{}:{}".format(lane, tag), data={'lane': lane, 'msg': msg})

    def always_warn_rule(self, tag, lane, percent_on_lane, **kwargs):
        """
        We always want to warn about an index that is significantly represented. This rule
        will make sure that we do so, and all other rules will contribute extra information
        if there is any.
        :param tag:
        :param lane:
        :param percent_on_lane:
        :return:
        """
        if self._tag_in_white_list(tag):
            msg = ("Index: {} on lane: {} was significantly overrepresented ({:.1f}%) at a " +
                   "significance threshold of {}%. " +
                   "This index is white-listed.").format(tag,
                                                         lane,
                                                         percent_on_lane,
                                                         self.qc_config["significance_threshold"])
            yield QCErrorWarning(msg=msg, ordering="{}:{}".format(lane, tag), data={'lane': lane, 'msg': msg})
        else:
            yield from UnidentifiedIndexHandler.\
                yield_qc_warning_with_message("Index: {} on lane: {} was significantly "
                                              "overrepresented ({:.1f}%) at significance "
                                              "threshold of: {}%.".format(tag,
                                                                          lane,
                                                                          percent_on_lane,
                                                                          self.qc_config["significance_threshold"]),
                                              lane,
                                              tag)

    @staticmethod
    def check_swapped_dual_index(tag, lane, samplesheet_searcher, **kwargs):
        if '+' in tag:
            split_tag = tag.split('+')
            swapped_tag = '{}+{}'.format(split_tag[1], split_tag[0])
            hits = samplesheet_searcher.exact_index_in_samplesheet(swapped_tag)
            for hit in hits:
                msg = '\tIt appears that maybe the dual index tag: {} was swapped. There was a hit for' \
                      ' the swapped index: {} at: {}'.format(tag, swapped_tag, hit)
                yield from UnidentifiedIndexHandler.yield_qc_warning_with_message(msg, lane, tag)

    @staticmethod
    def check_reversed_in_dual_index(tag, lane, samplesheet_searcher, **kwargs):
        if '+' in tag:
            split_tags = tag.split('+')
            for single_tag in split_tags:
                hits = samplesheet_searcher.one_index_match_from_dual_index_in_samplesheet(single_tag[::-1])
                for hit in hits:
                    msg = '\tWe found a possible match for the reverse of tag: {}, on: {}. '.format(single_tag, hit)
                    yield from UnidentifiedIndexHandler.yield_qc_warning_with_message(msg, lane, tag)

    @staticmethod
    def check_reverse_complement_in_dual_index(tag, lane, samplesheet_searcher, **kwargs):
        if '+' in tag:
            split_tags = tag.split('+')
            for single_tag in split_tags:
                hits = samplesheet_searcher.one_index_match_from_dual_index_in_samplesheet(
                    UnidentifiedIndexHandler.get_complementary_sequence(single_tag)[::-1])
                for hit in hits:
                    msg = '\tWe found a possible match for the reverse complement of tag: {}, on: {}. '.format(single_tag, hit)
                    yield from UnidentifiedIndexHandler.yield_qc_warning_with_message(msg, lane, tag)

    @staticmethod
    def check_complement_in_dual_index(tag, lane, samplesheet_searcher, **kwargs):
        if '+' in tag:
            split_tags = tag.split('+')
            for single_tag in split_tags:
                hits = samplesheet_searcher.exact_index_in_samplesheet(
                    UnidentifiedIndexHandler.get_complementary_sequence(single_tag))
                for hit in hits:
                    msg = '\tWe found a possible match for the complement of tag: {}, on: {}. '.format(single_tag, hit)
                    yield from UnidentifiedIndexHandler.yield_qc_warning_with_message(msg, lane, tag)

    @staticmethod
    def check_reversed_index(tag, lane, samplesheet_searcher, **kwargs):
        hits = samplesheet_searcher.exact_index_in_samplesheet(tag[::-1])
        for hit in hits:
            msg = '\tWe found a possible match for the reverse of tag: {}, on: {}'.format(tag, hit)
            yield from UnidentifiedIndexHandler.yield_qc_warning_with_message(msg, lane, tag)

    @staticmethod
    def check_reverse_complement_index(tag, lane, samplesheet_searcher, **kwargs):
        hits = samplesheet_searcher.exact_index_in_samplesheet(
            UnidentifiedIndexHandler.get_complementary_sequence(tag)[::-1])
        for hit in hits:
            msg = '\tWe found a possible match for the reverse complement of tag: {}, on: {}'.format(tag, hit)
            yield from UnidentifiedIndexHandler.yield_qc_warning_with_message(msg, lane, tag)

    @staticmethod
    def check_complement_index(tag, lane, samplesheet_searcher, **kwargs):
        hits = samplesheet_searcher.exact_index_in_samplesheet(
            UnidentifiedIndexHandler.get_complementary_sequence(tag))
        for hit in hits:
            msg = '\tWe found a possible match for the complementary of tag: {}, on: {}'.format(tag, hit)
            yield from UnidentifiedIndexHandler.yield_qc_warning_with_message(msg, lane, tag)

    @staticmethod
    def check_if_index_in_other_lane(tag, lane, samplesheet_searcher, **kwargs):
        hits = samplesheet_searcher.exact_index_in_samplesheet(tag)
        for hit in hits:
            msg = '\tWe found a possible match for the tag: {}, on another lane: {}'.format(tag, hit)
            yield from UnidentifiedIndexHandler.yield_qc_warning_with_message(msg, lane, tag)

    def number_of_reads_per_lane(self):
        """
        Transform conversion results into dict of lane -> total clusters pass filer
        :return: dict {<lane>: <total clusters pass filer>}
        """
        nbr_of_reads_per_lane = {}
        for lane_dict in self.conversion_results:
            nbr_of_reads_per_lane[int(lane_dict["LaneNumber"])] = int(lane_dict["TotalClustersPF"])
        return nbr_of_reads_per_lane

    @staticmethod
    def get_complementary_sequence(seq):
        conv_table = {'A': 'T', 'T': 'A', 'G': 'C', 'C': 'G', 'N': 'N', '+': '+'}
        comp_seq = ''
        for c in seq:
            comp_seq += conv_table[c]
        return comp_seq


class _SamplesheetSearcher(object):

    class SearchHit(object):
        def __init__(self, search_index, found_sample, found_lane):
            self.search_index = search_index
            self.found_sample = found_sample
            self.found_lane = found_lane

        def __str__(self):
            return "Lane: {}, for sample: {}. The tag we found in the samplesheet was: {}".format(self.found_lane,
                                                                               self.found_sample,
                                                                               self.search_index)

        def __eq__(self, other):
            if isinstance(other, self.__class__) and self.search_index == other.search_index \
                    and self.found_sample == other.found_sample and self.found_lane == other.found_lane:
                return True
            else:
                return False

        def __hash__(self):
            return hash(self.__class__.__name__ + self.search_index + self.found_sample + self.found_lane)

    def __init__(self, samplesheet):
        self.samplesheet_dict = self.transform_samplesheet_to_dict(samplesheet)

    @staticmethod
    def transform_samplesheet_to_dict(samplesheet):
        """
        Transform samplesheet to dict on form {index -> {lane -> sample name}}
        :param samplesheet:
        :return: dict of index, lane and sample name
        """

        samplesheet_dict = defaultdict(lambda: defaultdict(dict))
        for s in samplesheet:
            index = s['index']
            if s.get('index2'):
                index += '+{}'.format(s['index2'])
            # MiSeqs for example do not have lanes in their samplesheets, thus we will default to using lane 1
            # if nothing has been specified in the samplesheet. /JD 20181101
            lane = s.get('Lane', '1')
            samplesheet_dict[index][lane] = s['Sample_Name']

        return samplesheet_dict

    def exact_index_in_samplesheet(self, index):
        """
        Search the sample sheet dict for an index to find which lane and which sample
        it is associated with.
        :param index:
        :return: generator of SearchHits
        """
        index_hits = self.samplesheet_dict.get(index)
        if index_hits:
            for lane, sample in index_hits.items():
                yield _SamplesheetSearcher.SearchHit(index, sample, lane)

    def one_index_match_from_dual_index_in_samplesheet(self, index):
        """
        Search for in-exact matches in samplesheet, i.e. hits where there is a hit, for one, but not
        both indexes in a dual index tag.
        :param index:
        :return:
        """

        for samplesheet_index in self.samplesheet_dict.keys():
            if index in set(samplesheet_index.split('+')):
                for lane, sample in self.samplesheet_dict[samplesheet_index].items():
                    yield _SamplesheetSearcher.SearchHit(index, sample, lane)
