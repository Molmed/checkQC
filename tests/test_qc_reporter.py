from unittest import mock
from collections import namedtuple

import pytest

from checkQC.handlers.qc_handler import QCErrorFatal, QCErrorWarning
from checkQC.qc_reporter import QCReporter


@pytest.fixture
def qc_data():
    return namedtuple("QCData", ["instrument", "read_length"])("novaseq_SP", 36)


@pytest.fixture
def checker_configs():
    return {
        "default_handlers": [
            {"name": "mock_checker", "error": 2, "warning": 1},
            {"name": "mock_checker_bis", "error": 0, "warning": 1},
        ],
        "novaseq_SP": {
            "37-39": {
                "view": "mock_view",
                "handlers": [
                    {"name": "mock_checker", "error": 6, "warning": 2},
                ],
            },
            "36": {
                "view": "mock_view",
                "handlers": [
                    {"name": "mock_checker", "error": 5, "warning": 2},
                ],
            },
        },
    }


@pytest.fixture
def qc_reporter(checker_configs):
    with mock.patch("checkQC.qc_checkers") as qc_checkers:
        with mock.patch("checkQC.views") as qc_views:
            qc_reporter = QCReporter(checker_configs)

            def checker_generator(name):
                def checker(self, error_threshold, warning_threshold):
                    if error_threshold != "unknown":
                        return [QCErrorFatal(f"{name}={error_threshold}")]
                    else:
                        return [QCErrorWarning(f"{name}={warning_threshold}")]
                return checker

            qc_checkers.mock_checker = checker_generator("mock_checker")
            qc_checkers.mock_checker_bis = checker_generator("mock_checker_bis")
            qc_views.mock_view = lambda checker_configs, qc_data, qc_reports: qc_reports

            yield qc_reporter


def test_report(qc_reporter, qc_data):
    exit_status, reports = qc_reporter.gather_reports(
        qc_data,
    )

    assert exit_status == 1
    assert len(reports) == 2
    assert any("mock_checker=5" in str(report) for report in reports)
    assert any("mock_checker_bis=0" in str(report) for report in reports)
    assert all(report.type() == "error" for report in reports)


def test_downgrade_errors(qc_reporter, qc_data):
    exit_status, reports = qc_reporter.gather_reports(
        qc_data,
        downgrade_errors_for=["mock_checker", "mock_checker_bis"],
    )

    assert exit_status == 0
    assert len(reports) == 2
    assert any("mock_checker=5" in str(report) for report in reports)
    assert any("mock_checker_bis=0" in str(report) for report in reports)
    assert all(report.type() == "warning" for report in reports)


def test_report_range_read_len(qc_reporter, qc_data):
    qc_data = qc_data._replace(read_length=38)

    exit_status, reports = qc_reporter.gather_reports(qc_data)

    assert exit_status == 1
    assert len(reports) == 2
    assert any("mock_checker=6" in str(report) for report in reports)
    assert any("mock_checker_bis=0" in str(report) for report in reports)


def test_report_use_closest_read_len(qc_reporter, qc_data):
    qc_data = qc_data._replace(read_length=35)

    with pytest.raises(KeyError):
        exit_status, reports = qc_reporter.gather_reports(qc_data)
    exit_status, reports = qc_reporter.gather_reports(
            qc_data, use_closest_read_len=True)

    assert exit_status == 1
    assert len(reports) == 2
    assert any("mock_checker=5" in str(report) for report in reports)
    assert any("mock_checker_bis=0" in str(report) for report in reports)
