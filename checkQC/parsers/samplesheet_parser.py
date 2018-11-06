
from pathlib import Path

from sample_sheet import SampleSheet

from checkQC.parsers.parser import Parser
from checkQC.exceptions import ConfigurationError, SamplesheetNotFound


class SamplesheetParser(Parser):
    """
    TODO
    """

    def __init__(self, runfolder, parser_configurations, *args, **kwargs):
        """
        Create a SamplesheetParser instance for the specified runfolder
        :param runfolder: path to the runfolder to parse
        :param parser_configurations: dict containing any extra configuration required by
        the parser under class name key
        """
        super().__init__(*args, **kwargs)

        self.runfolder = runfolder

        self.parser_conf = parser_configurations.get(self.__class__.__name__)
        if not self.parser_conf:
            raise ConfigurationError("The configuration must contain parser_configurations "
                                     "key with subkey SamplesheetParser. E.g: \n"
                                     "parser_configurations:\n"
                                     "\tSamplesheetParser:\n"
                                     "\t\tsamplesheet_name: Samplesheet.csv")

        self._samplesheet_name = self.parser_conf.get("samplesheet_name")
        if not self._samplesheet_name:
            raise ConfigurationError("The configuration must contain the key samplesheet_name, specifying "
                                     "what the name of the samplesheet is.")

        self._samplesheet = Path(self.runfolder, self._samplesheet_name)
        if not self._samplesheet.exists():
            raise SamplesheetNotFound("Could not identify samplesheet at: {}".format(self._samplesheet))

    def run(self):
        samplesheet_read = SampleSheet(self._samplesheet)
        self._send_to_subscribers(("samplesheet", samplesheet_read))

    def __eq__(self, other):
        if isinstance(other, self.__class__) and self.runfolder == other.runfolder:
            return True
        else:
            return False

    def __hash__(self):
        return hash(self.__class__.__name__ + self.runfolder)
