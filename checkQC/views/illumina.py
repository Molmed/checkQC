from itertools import groupby


def illumina_view(qc_reports):
    """
    Group reports by lane and by read
    """
    lane_reports = {
        "lane reports": {
            lane: {
                "read reports": {
                    read: list(read_report)
                    for read, read_report in groupby(
                        lane_reports,
                        key=lambda report: report.data.get("read"))
                    if read
                },
                "other reports": [
                    report
                    for report in lane_reports
                    if "read" not in report.data
                ]
            }
            for lane, lane_reports in groupby(
                qc_reports,
                key=lambda report: report.data.get("lane"))
            if lane
        },
        "other reports": [
            report
            for report in qc_reports
            if "lane" not in report.data
        ]
    }

    return lane_reports
