
import logging

log = logging.getLogger(__name__)


class RunTypeSummarizer(object):

    @staticmethod
    def summarize(instrument_and_reagent_version, read_lengths, handler_config):

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
            name = handler["name"]
            error = handler["error"]
            warning = handler["warning"]
            log.info("\t{} Error={} Warning={}".format(name, error, warning))
            summary["handlers"].append({"handler": name, "error": error, "warning": warning})

        return summary
