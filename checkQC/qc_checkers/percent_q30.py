from checkQC.handlers.qc_handler import QCErrorFatal, QCErrorWarning


def percent_q30(
        qc_data,
        error_threshold,
        warning_threshold
):
    """
    Check that the percent of bases on a lane and reads with Q30 or high was
    above the specified threshold.
    """
    assert qc_data.sequencing_metrics
    assert (
        (error_threshold == "unknown" or warning_threshold == "unknown")
        or error_threshold < warning_threshold
    )

    def _qualify_q30(q30, lane, read, is_index_read):
        data = {
            "lane": lane,
            "read": read,
            "q30": q30,
        }

        read_or_index_text = "read (I)" if is_index_read else "read"
        msg = ("%Q30 {q30} was too low on lane: {lane} "
               "for {read_or_index_text}: {read}")

        if (q30 and error_threshold != "unknown" and
                q30 < error_threshold):
            data["threshold"] = error_threshold
            return QCErrorFatal(
                msg.format(**data, read_or_index_text=read_or_index_text),
                data=data
            )
        if (q30 and warning_threshold != "unknown"  and
                q30 < warning_threshold):
            data["threshold"] = warning_threshold
            return QCErrorWarning(
                msg.format(**data, read_or_index_text=read_or_index_text),
                data=data
            )


    return [
        qc_report
        for lane, lane_data in qc_data.sequencing_metrics.items()
        for read, read_data in lane_data["reads"].items()
        if (qc_report := _qualify_q30(
            read_data["percent_q30"], lane, read, read_data["is_index"]
            )
        )
    ]


