from checkQC.handlers.qc_handler import QCErrorFatal, QCErrorWarning


def cluster_pf(
    self,
    error_threshold,
    warning_threshold
):
    assert self.sequencing_metrics
    assert (
        (error_threshold == "unknown" or warning_threshold == "unknown")
        or error_threshold < warning_threshold
    )

    def _qualify_error(total_cluster_pf, lane):
        data = {
            "lane": lane,
            "total_cluster_pf": total_cluster_pf,
        }
        msg = "Clusters PF {total_cluster_pf} > {threshold} on lane {lane}"

        match total_cluster_pf:
            case total_cluster_pf if (
                    error_threshold != "unknown"
                    and total_cluster_pf < error_threshold
                ):
                    data["threshold"] = error_threshold
                    return QCErrorFatal(msg.format(**data), data=data)
            case total_cluster_pf if (
                    warning_threshold != "unknown"
                    and total_cluster_pf < warning_threshold
                ):
                    data["threshold"] = warning_threshold
                    return QCErrorWarning(msg.format(**data), data=data)

    return [
        qc_report
        for lane, lane_data in self.sequencing_metrics.items()
        if (qc_report := _qualify_error(lane_data["total_cluster_pf"], lane))
    ]

