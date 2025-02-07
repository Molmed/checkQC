import re
import logging

from checkQC.qc_checkers.utils import handler2checker


log = logging.getLogger(__name__)


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

        self.exit_status = 0

    from checkQC.parsers.illumina import from_bclconvert

    from checkQC.qc_checkers import cluster_pf
    from checkQC.qc_checkers import error_rate
    from checkQC.qc_checkers import reads_per_sample

    from checkQC.views.illumina import illumina_view

    def report(self, use_closest_read_len=False, downgrade_errors_for=[]):
        config = self._get_config(
            configs,
            use_closest_read_len,
            downgrade_errors_for,
        )
        checker_configs = config["checkers"]

        qc_reports = [
            qc_report
            for checker, checker_config in checker_configs.items()
            for qc_report in getattr(self, handler2checker(checker))(self, **checker_config)
        ]

        if any(qc_report["status"] == "error" for qc_report in qc_reports):
            self.exit_status = 1

        return getattr(self, config["view"])(self, qc_reports)

    def _get_checkers_config(
            self,
            configs,
            use_closest_read_len,
            downgrade_errors_for,
        ):
        best_match_read_len = self._select_read_len(configs, use_closest_read_len)
        checker_configs = self._reformat_config(configs, best_match_read_len)
        checker_configs = self._downgrade_errors(checker_configs, downgrade_errors_for)

        return {
            "checkers": checker_configs,
            "view": configs.get("view", "illumina_view")
        }

    def _select_read_len(self, configs, use_closest_read_len):
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

        best_match_read_len = min(configs[self.instrument], key=dist)

        if not use_closest_read_len and dist(best_match_read_len) > 0:
            raise KeyError(
                f"No config entry matching read length {self.read_length}"
                f"found for instrument {self.instrument}."
            )

        return best_match_read_len

    def _reformat_config(self, configs, best_match_read_len):
        return {
            checker_config["name"]: {
                f"{k}_threshold" if k in ["error", "warning"] else k: v
                for k, v in checker_config.items()
                if k != "name"
            }
            for checker_config in (
                configs.get("default_handlers", [])
                + configs[self.instrument][best_match_read_len]["handlers"]
        }

    def _downgrade_errors(self, checker_configs, downgrade_errors_for):
        for checker in downgrade_errors_for:
            if (
                checker not in checker_configs
                or checker_configs[checker]["error_threshold"] == "unknown"
            ):
                    continue
                log.info(f"Downgrading errors for {checker} to warnings.")
                checker_config = checker_configs.get[checker]
                checker_config["warning_threshold"] = checker_config["error_threshold"]
                checker_config["error_threshold"] = "unknown"

        return checker_configs


