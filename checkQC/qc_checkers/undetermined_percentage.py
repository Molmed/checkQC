import numpy as np

from checkQC.handlers.qc_handler import QCErrorFatal, QCErrorWarning


def undetermined_percentage(
    qc_data,
    error_threshold,
    warning_threshold,
):
    """
    Check percentage of undetermined reads per lane
    """
    assert qc_data.sequencing_metrics
    assert (
        (error_threshold == "unknown" or warning_threshold == "unknown")
        or error_threshold > warning_threshold
    )

    def _qualify_error(lane_data, lane):
        data = {
            "lane": lane,
            "qc_checker": "undetermined_percentage",
        }
        if lane_data["yield"] == 0:
            data["percentage_undetermined"] = None
            return QCErrorFatal(
                f"Yield for lane {lane} was 0. "
                "No undetermined percentage could be computed",
                data=data,
            )

        mean_percent_phix_aligned = np.nan_to_num(np.nanmean(
            [
                read_data["mean_percent_phix_aligned"]
                for read_data in lane_data["reads"].values()
            ]
        ), nan=0.0)

        # NOTE this includes the mean percentage phiX
        percentage_undetermined = (
            lane_data["yield_undetermined"] / lane_data["yield"] * 100
        )

        data["percentage_undetermined"] = percentage_undetermined
        data["mean_percent_phix_aligned"] = mean_percent_phix_aligned

        msg = (
            "Percentage of undetermined indices "
            "{percentage_undetermined:.2f}% (- {mean_percent_phix_aligned:.2f}% phiX) "
            "> {threshold:.2f}% "
            "on lane {lane}."
        )

        match percentage_undetermined:
            case percentage_undetermined if (
                error_threshold != "unknown"
                and percentage_undetermined - mean_percent_phix_aligned > error_threshold
            ):
                data["threshold"] = error_threshold
                return QCErrorFatal(msg.format(**data), data=data)
            case percentage_undetermined if (
                warning_threshold != "unknown"
                and percentage_undetermined - mean_percent_phix_aligned > warning_threshold
            ):
                data["threshold"] = warning_threshold
                return QCErrorWarning(msg.format(**data), data=data)

    return [
        qc_report
        for lane, lane_data in qc_data.sequencing_metrics.items()
        if (qc_report := _qualify_error(lane_data, lane))
    ]
