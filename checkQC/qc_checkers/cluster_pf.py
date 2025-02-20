from checkQC.handlers.qc_handler import QCErrorFatal, QCErrorWarning


def cluster_pf(
    qc_data,
    error_threshold,
    warning_threshold
):
    assert qc_data.sequencing_metrics
    assert (
        (error_threshold == "unknown" or warning_threshold == "unknown")
        or error_threshold < warning_threshold
    )

    if error_threshold != "unknown":
        error_threshold = int(error_threshold * 10**6)
    if warning_threshold != "unknown":
        warning_threshold = int(warning_threshold * 10**6)

    def format_msg(total_cluster_pf, threshold, lane):
        return f"Clusters PF {total_cluster_pf / 10**6}M < {threshold / 10**6}M on lane {lane}"

    def _qualify_error(total_cluster_pf, lane):
        data = {
            "lane": lane,
            "total_cluster_pf": total_cluster_pf,
        }

        match total_cluster_pf:
            case total_cluster_pf if (
                    error_threshold != "unknown"
                    and total_cluster_pf < error_threshold
                ):
                    data["threshold"] = error_threshold
                    return QCErrorFatal(format_msg(**data), data=data)
            case total_cluster_pf if (
                    warning_threshold != "unknown"
                    and total_cluster_pf < warning_threshold
                ):
                    data["threshold"] = warning_threshold
                    return QCErrorWarning(format_msg(**data), data=data)

    return [
        qc_report
        for lane, lane_data in qc_data.sequencing_metrics.items()
        if (qc_report := _qualify_error(lane_data["total_cluster_pf"], lane))
    ]

