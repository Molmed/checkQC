
import logging

log = logging.getLogger(__name__)


class RunTypeSummarizer(object):
    """
    RunTypeSummarizer contains methods used to summarize information about a run (mostly in order
    to be able to report this back to the user in one for or another).
    """

    @staticmethod
    def summarize(instrument_and_reagent_version, read_lengths, handler_config):
        """
        Utility method to parse log and summarize the information about a particular run.
        This is used to tell the user what information CheckQC has gathered about a run, and
        what configuration was used.

        :param instrument_and_reagent_version: str with instrument and reagent version
        :param read_lengths: str with read length
        :param handler_config: dict with handler configuration
        :returns: dict with information on the handlers used
        """

        summary = {}

        log.info("Run summary")
        log.info("-----------")
        log.info("Instrument and reagent version: {}".format(instrument_and_reagent_version))
        summary["instrument_and_reagent_type"] = instrument_and_reagent_version
        log.info("Read length: {}".format(read_lengths))
        summary["read_length"] = read_lengths
        log.info("Enabled handlers and their config values were: ")
        summary["handlers"] = []
        for handler in handler_config:
            log.info("\t{}".format(handler))
            summary["handlers"].append(handler)

        return summary
