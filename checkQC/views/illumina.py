from itertools import groupby
import json
import yaml


def illumina_data_view(checker_configs, qc_data, qc_reports):
    """
    Output the report's data, grouped by lanes and checker type, in json
    format.
    """
    data = format_data(
        checker_configs, qc_data, qc_reports,
        format_report=lambda report: report.as_dict(),
    )

    return json.dumps(data, indent=True)


def illumina_short_view(checker_configs, qc_data, qc_reports):
    """
    Output the report's messages, grouped by lanes and checker type, in yaml
    format.
    """
    data = format_data(checker_configs, qc_data, qc_reports, format_report=str)

    return yaml.safe_dump(data)


def format_data(checker_configs, qc_data, qc_reports, format_report=str):
    """
    Group reports by lane and checker type.
    """
    assert all("lane" in report.data for report in qc_reports)

    return {
        "lane_reports": {
            lane: {
                qc_checker: [format_report(report) for report in reports]
                for qc_checker, reports in group_reports(
                    lane_reports,
                    key=lambda report: report.data["qc_checker"],
                )
            }
            for lane, lane_reports in group_reports(
                qc_reports,
                key=lambda report: report.data["lane"]
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
