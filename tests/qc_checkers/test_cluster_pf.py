from collections import namedtuple
import pytest

from checkQC.qc_checkers.cluster_pf import cluster_pf
from checkQC.handlers.qc_handler import QCErrorFatal, QCErrorWarning

@pytest.fixture
def qc_data():
    return namedtuple("QCData", "sequencing_metrics")(
        {
            1: {"total_reads_pf":  1_000_000_000},
            2: {"total_reads_pf":     10_000_000},
            3: {"total_reads_pf":    100_000_000},
            4: {"total_reads_pf": 10_000_000_000},
        }
    )


def format_msg(total_reads_pf, threshold, lane, **kwargs):
    return f"Clusters PF {total_reads_pf / 10**6}M < {threshold / 10**6}M on lane {lane}"


def test_cluster_pf(qc_data):
    qc_reports = cluster_pf(
        qc_data,
        error_threshold=50,
        warning_threshold=500.5,
    )

    assert len(qc_reports) == 2
    assert None not in qc_reports
    for report in qc_reports:
        lane, threshold = report.data["lane"], report.data["threshold"]
        match lane:
            case 2:
                exp_data = {
                    "total_reads_pf": qc_data.sequencing_metrics[lane]["total_reads_pf"],
                    "threshold": 50_000_000,
                    "lane": lane,
                    "qc_checker": "cluster_pf",
                }
                assert report.message == format_msg(**exp_data)
                assert report.type() == "error"
                assert report.data == exp_data
            case 3:
                exp_data = {
                    "total_reads_pf": qc_data.sequencing_metrics[lane]["total_reads_pf"],
                    "threshold": 500_500_000,
                    "lane": lane,
                    "qc_checker": "cluster_pf",
                }
                assert report.message == format_msg(**exp_data)
                assert report.type() == "warning"
                assert report.data == exp_data
            case _:
                raise ValueError(f"Lane {lane} unexpectedly didn't pass QC check.")

def test_cluster_pf_error_unknown(qc_data):
    qc_reports = cluster_pf(
        qc_data,
        error_threshold="unknown",
        warning_threshold=500,
    )

    assert len(qc_reports) == 2
    assert None not in qc_reports
    for report in qc_reports:
        lane, threshold = report.data["lane"], report.data["threshold"]
        match lane:
            case 2:
                exp_data = {
                    "total_reads_pf": qc_data.sequencing_metrics[lane]["total_reads_pf"],
                    "threshold": 500_000_000,
                    "lane": lane,
                    "qc_checker": "cluster_pf",
                }
                assert report.message == format_msg(**exp_data)
                assert report.type() == "warning"
                assert report.data == exp_data
            case 3:
                exp_data = {
                    "total_reads_pf": qc_data.sequencing_metrics[lane]["total_reads_pf"],
                    "threshold": 500_000_000,
                    "lane": lane,
                    "qc_checker": "cluster_pf",
                }
                assert report.message == format_msg(**exp_data)
                assert report.type() == "warning"
                assert report.data == exp_data
            case _:
                raise ValueError(f"Lane {lane} unexpectedly didn't pass QC check.")

def test_cluster_pf_warning_unknown(qc_data):
    qc_reports = cluster_pf(
        qc_data,
        error_threshold=50,
        warning_threshold="unknown",
    )

    assert len(qc_reports) == 1
    assert None not in qc_reports
    report = qc_reports[0]
    lane, threshold = report.data["lane"], report.data["threshold"]
    match lane:
        case 2:
            exp_data = {
                "total_reads_pf": qc_data.sequencing_metrics[lane]["total_reads_pf"],
                "threshold": 50_000_000,
                "lane": lane,
                "qc_checker": "cluster_pf",
            }
            assert report.message == format_msg(**exp_data)
            assert report.type() == "error"
            assert report.data == exp_data
        case _:
            raise ValueError(f"Lane {lane} unexpectedly didn't pass QC check.")
