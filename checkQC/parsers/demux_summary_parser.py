
from pathlib import Path

from checkQC.runfolder_reader import RunfolderReader
from checkQC.parsers.parser import Parser
from checkQC.exceptions import ConfigurationError, DemuxSummaryNotFound


class DemuxSummaryParser(Parser):
    """
    The DemuxSummaryParser will read information from the DemuxSummaryF1L<Lane number>.txt files.
    At the moment it fetches the information about 'Most Popular Unknown Index Sequences'.

    It will send the information lane wise as a tuple on the format:
     ("index_counts", {"lane": <lane nbr>, "indices": [<{"index": <index string>, "count": <nbr>}>]}
    """

    def __init__(self, runfolder, parser_configurations, *args, **kwargs):
        """
        Create a DemuxSummaryParser instance for the specified runfolder
        :param runfolder: path to the runfolder to parse
        :param parser_configurations: dict containing any extra configuration required by
        the parser under class name key
        """
        super().__init__(*args, **kwargs)

        self.runfolder = runfolder

        # NOTE: This parser will use the same config entry a the StatsJsonParser in order
        #       to not break backward compatibility. And it feel unnecessary to add this
        #       value to the config twice. /JD 2018-09-14
        self.parser_conf = parser_configurations.get("StatsJsonParser")
        if not self.parser_conf:
            raise ConfigurationError("The configuration must contain parser_configurations "
                                     "key with subkey StatsJsonParser. E.g: \n"
                                     "parser_configurations:\n"
                                     "\tStatsJsonParser:\n"
                                     "\t\tbcl2fastq_output_path: Data/Intensities/BaseCalls")

        self._bcl2fastq_output_path = self.parser_conf.get("bcl2fastq_output_path")
        if not self._bcl2fastq_output_path:
            raise ConfigurationError("The configuration must contain the key bcl2fastq_output_path, specifying "
                                     "where the bcl2fastq output is, relative to the runfolder root.")

        self._nbr_of_lanes = RunfolderReader.get_nbr_of_lanes(self.runfolder)
        self._validate_demux_summary_files_exist(self.runfolder, self._bcl2fastq_output_path)

    def _validate_demux_summary_files_exist(self, runfolder, bcl2fastq_output_path):
        for i in range(1, self._nbr_of_lanes):
            path = Path(runfolder, bcl2fastq_output_path, 'Stats', 'DemuxSummaryF1L{}.txt'.format(i))
            if not path.exists():
                raise DemuxSummaryNotFound("Could not identify expected demux summary file: {}. "
                                           "We expect to find {} files matching the pattern, "
                                           "'DemuxSummaryF1L<Lane number>.txt'".format(path))

    @staticmethod
    def _read_most_popular_unknown_indexes(demux_summary_file):
        with open(demux_summary_file, 'r') as f:
            reached_data = False
            for line in f:
                if reached_data:
                    split_data = line.split('\t')
                    yield {'index': split_data[0].strip(), 'count': int(split_data[1].strip())}
                if line.startswith("### Columns: Index_Sequence Hit_Count"):
                    reached_data = True

    def run(self):
        for i in range(1, self._nbr_of_lanes+1):
            path = Path(self.runfolder, self._bcl2fastq_output_path, 'Stats', 'DemuxSummaryF1L{}.txt'.format(i))
            self._send_to_subscribers(("index_counts",
                                       {"lane": i, "indices": list(self._read_most_popular_unknown_indexes(path))}))

    def __eq__(self, other):
        if isinstance(other, self.__class__) and self.runfolder == other.runfolder:
            return True
        else:
            return False

    def __hash__(self):
        return hash(self.__class__.__name__ + self.runfolder)
