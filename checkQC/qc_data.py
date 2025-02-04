import re

from checkQC.qc_checkers.utils import handler2checker


class QCData:
    def __init__(
        self,
        instrument,
        read_length,
        samplesheet,
        sequencing_metrics,  # TODO validate dict content
        # The schema will define mandatory fields but may evolve over time with
        # new instruments
    ):
        self.instrument = instrument
        self.read_length = read_length
        self.samplesheet = samplesheet
        self.sequencing_metrics = sequencing_metrics

    from checkQC.parsers.illumina import from_bclconvert

    from checkQC.qc_checkers import error_rate, reads_per_sample

    from checkQC.views.illumina import illumina_view

    def report(self, configs, use_closest_read_len=False):
        config = self._get_config(configs[self.instrument], use_closest_read_len)

        checker_configs = {
            checker_config["name"]: {
                f"{k}_threshold" if k in ["error", "warning"] else k: v
                for k, v in checker_config.items()
                if k != "name"
            }
            for checker_config in configs.get("default_handlers", []) + config["handlers"]
        }

        qc_reports = [
            qc_report
            for checker, checker_config in checker_configs.items()
            for qc_report in getattr(self, handler2checker(checker))(self, **checker_config)
        ]

        return getattr(self, config.get("view", "illumina_view"))(self, qc_reports)

    def _get_config(self, instrument_configs, use_closest_read_len):
        def dist(read_len):
            if mtch := re.match(r"(\d+)-(\d+)", read_len):
                low, high = (int(n) for n in mtch.groups())
                return (
                    0
                    if low <= self.read_length <= high
                    else min(
                        abs(low - self.read_length),
                        abs(high - self.read_length)
                    )
                )
            else:
                return abs(int(read_len) - self.read_length)

        best_match_read_len = min(instrument_configs, key=dist)

        if not use_closest_read_len and dist(best_match_read_len) > 0:
            raise KeyError(
                f"No config entry matching read length {self.read_length}"
                f"found for instrument {self.instrument}."
            )

        return instrument_configs[best_match_read_len]
