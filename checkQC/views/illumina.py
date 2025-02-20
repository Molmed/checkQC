from itertools import groupby


def illumina_view(checker_configs, qc_data, qc_reports):
    """
    Group reports by lane and by read
    """
    return {
        "lane reports": {
            lane: {
                "read reports": {
                    read: [
                        str(report)
                        for report in read_reports
                    ]
                    for read, read_reports in group_reports(
                        lane_reports,
                        key=lambda report: report.data.get("read")
                    )
                },
                "other reports": [
                    str(report)
                    for report in lane_reports
                    if "read" not in report.data
                ]
            }
            for lane, lane_reports in group_reports(
                qc_reports,
                key=lambda report: report.data.get("lane")
            )
        },
        "other reports": [
            str(report)
            for report in qc_reports
            if "lane" not in report.data
        ],
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
