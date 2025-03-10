import numpy as np

from checkQC.handlers.qc_handler import QCErrorFatal, QCErrorWarning


def error_rate(
        qc_data,
        error_threshold,
        warning_threshold,
        allow_missing_error_rate=False,
):
    """
    Check error rate for each lane and read.

    Sometimes, error rate will be 0. or nan (e.g. when no PhiX has been loaded
    on the lane). Use `allow_missing_error_rate` to allow these values.
    """
    assert qc_data.sequencing_metrics
    assert (
        (error_threshold == "unknown" or warning_threshold == "unknown")
        or error_threshold > warning_threshold
    )

    def _qualify_error(error, lane, read):
        data = {
            "lane": lane,
            "read": read,
            "error": error,
        }
        msg = "Error rate {error} > {threshold} on lane {lane} for read {read}."

        match error:
            case error if (np.isnan(error) or error == 0.) and not allow_missing_error_rate:
                return QCErrorFatal(
                    f"Error rate is {error} on lane {lane} for read {read}. "
                    "This may be because no PhiX was loaded on this lane. "
                    "Use \"allow_missing_error_rate: true\" to disable this error message.",
                    data=data,
                )
            case error if error_threshold != "unknown" and error > error_threshold:
                data["threshold"] = error_threshold
                return QCErrorFatal(msg.format(**data), data=data)
            case error if warning_threshold != "unknown" and error > warning_threshold:
                data["threshold"] = warning_threshold
                return QCErrorWarning(msg.format(**data), data=data)

    return [
        qc_report
        for lane, lane_data in qc_data.sequencing_metrics.items()
        for read, read_data in lane_data["reads"].items()
        if (qc_report := _qualify_error(read_data["mean_error_rate"], lane, read))
    ]


