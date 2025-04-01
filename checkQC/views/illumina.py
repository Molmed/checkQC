from itertools import groupby


def illumina_view(checker_configs, qc_data, qc_reports):
    """
    Group reports by lane and by read
    """
    return {
        "lane reports": {
            lane: {
                qc_checker: [
                    str(report)
                    for report in reports
                ]
                for qc_checker, reports in group_reports(
                    lane_reports,
                    key=lambda report: report.data["qc_checker"],
                )
            }
            for lane, lane_reports in group_reports(
                qc_reports,
                key=lambda report: report.data.get("lane")
            )
        },
        "other reports": {
            qc_checker: non_lane_reports
            for qc_checker, reports in group_reports(
                qc_reports,
                key=lambda report: report.data["qc_checker"],
            )
            if (
                non_lane_reports := [
                    str(report)
                    for report in reports
                    if "lane" not in report.data
                ]
            )
        },
        "run_summary": {
            "instrument_and_reagent_version": qc_data.instrument,
            "read_length": qc_data.read_length,
            "checkers": checker_configs,
        }
    }

def group_reports(reports, key):
    reports = sorted(
        [
            report for report in reports
            if key(report)
        ],
        key=key
    )

    return [
        (k, list(k_reports_itr))
        for k, k_reports_itr in groupby(reports, key=key)
    ]
