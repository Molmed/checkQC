from checkQC.handlers.qc_handler import QCErrorFatal, QCErrorWarning


def reads_per_sample(
    qc_data,
    error_threshold,
    warning_threshold,
):
    """
    Check number of reads per sample
    """
    assert qc_data.sequencing_metrics
    assert (
        (error_threshold == "unknown" or warning_threshold == "unknown")
        or error_threshold < warning_threshold
    )

    def _qualify_error(lane, number_of_samples, sample_id, cluster_count):
        sample_reads = cluster_count / 10**6
        data = {
            "lane": lane,
            "number_of_samples": number_of_samples,
            "sample_id": sample_id,
            "sample_reads": sample_reads,
        }
        msg = "Number of reads for sample {sample_id} on lane {lane} were too low: "\
              "{sample_reads} M (threshold: {threshold} M)"

        match sample_reads:
            case sample_reads if (
                error_threshold != "unknown"
                and sample_reads < (
                    threshold := float(error_threshold) / number_of_samples
                    )
            ):
                data["threshold"] = threshold
                return QCErrorFatal(msg.format(**data), data=data)
            case sample_reads if (
                warning_threshold != "unknown"
                and sample_reads < (
                    threshold := float(warning_threshold) / number_of_samples
                    )
            ):
                data["threshold"] = threshold
                return QCErrorWarning(msg.format(**data), data=data)

    return [
        qc_report
        for lane, lane_data in qc_data.sequencing_metrics.items()
        for sample_data in lane_data["reads_per_sample"]
        if (
            qc_report := _qualify_error(
                lane,
                len(lane_data["reads_per_sample"]),
                sample_data["sample_id"],
                sample_data["cluster_count"],
            ),
        )
    ]
