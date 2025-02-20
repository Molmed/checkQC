import re
import logging

import checkQC.qc_checkers
import checkQC.views
from checkQC.qc_checkers.utils import handler2checker


log = logging.getLogger(__name__)


class QCReporter:
    """
    Class to generate QC reports based on QCData.
    """
    def __init__(
        self,
        configs,
    ):
        self.configs = configs

    def gather_reports(
        self,
        qc_data,
        use_closest_read_len=False,
        downgrade_errors_for=[],
    ):
        exit_status = 0

        config = self._select_configs(
            qc_data,
            use_closest_read_len,
            downgrade_errors_for,
        )
        checker_configs = config["checkers"]

        qc_reports = [
            qc_report
            for checker, checker_config in checker_configs.items()
            for qc_report in getattr(checkQC.qc_checkers, handler2checker(checker))(
                qc_data,
                **checker_config
            )
        ]

        if any(qc_report.type() == "error" for qc_report in qc_reports):
            exit_status = 1

        return exit_status, getattr(checkQC.views, config["view"])(
            checker_configs,
            qc_data,
            qc_reports,
        )

    def _select_configs(
        self,
        qc_data,
        use_closest_read_len,
        downgrade_errors_for,
    ):

        best_match_read_len = self._select_read_len(
            qc_data,
            use_closest_read_len,
        )

        checker_configs = self._get_checker_configs(
            qc_data,
            best_match_read_len,
            downgrade_errors_for,
        )

        return {
            "checkers": checker_configs,
            "view": self.configs[qc_data.instrument][best_match_read_len].get(
                "view", "illumina_view"),
        }

    def _select_read_len(self, qc_data, use_closest_read_len):
        def dist(read_len):
            if mtch := re.match(r"(\d+)-(\d+)", read_len):
                low, high = (int(n) for n in mtch.groups())
                return (
                    0
                    if low <= qc_data.read_length <= high
                    else min(
                        abs(low - qc_data.read_length),
                        abs(high - qc_data.read_length)
                    )
                )
            else:
                return abs(int(read_len) - qc_data.read_length)

        best_match_read_len = min(self.configs[qc_data.instrument], key=dist)

        if not use_closest_read_len and dist(best_match_read_len) > 0:
            raise KeyError(
                f"No config entry matching read length {qc_data.read_length}"
                f"found for instrument {qc_data.instrument}."
            )

        return best_match_read_len

    def _get_checker_configs(
        self,
        qc_data,
        best_match_read_len,
        downgrade_errors_for,
    ):
        checker_configs = {
            checker_config["name"]: {
                f"{k}_threshold" if k in ["error", "warning"] else k: v
                for k, v in checker_config.items()
                if k != "name"
            }
            for checker_config in (
                self.configs.get("default_handlers", [])
                + self.configs[qc_data.instrument][best_match_read_len]["handlers"]
            )
        }

        for checker in downgrade_errors_for:
            if (
                checker not in checker_configs
                or checker_configs[checker]["error_threshold"] == "unknown"
            ):
                continue
            log.info(f"Downgrading errors for {checker} to warnings.")
            checker_config = checker_configs.get(checker)
            checker_config["warning_threshold"] = checker_config["error_threshold"]
            checker_config["error_threshold"] = "unknown"

        return checker_configs
