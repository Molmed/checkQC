from collections import namedtuple

import pytest

from checkQC.views.illumina import illumina_view
from checkQC.handlers.qc_handler import QCErrorFatal, QCErrorWarning

@pytest.fixture
def qc_reports():
    return [
        QCErrorFatal("", data={"lane": 1, "read": 1}),
        QCErrorWarning("", data={"lane": 1, "read": 1}),
        QCErrorFatal("", data={"lane": 2}),
        QCErrorFatal("", data={"lane": 1, "read": 2}),
        QCErrorFatal("", data={}),
    ]


@pytest.fixture
def qc_data():
    return namedtuple("QCData", ["instrument", "read_length"])("novaseq_SP", 36)


@pytest.fixture
def checker_configs():
    return {
        "test_checker": {"error": 0, "warning": 0},
    }


def test_illumima_view(qc_reports, qc_data, checker_configs):
    result = illumina_view(checker_configs, qc_data, qc_reports)

    assert len(result["lane reports"]) == 2
    assert len(result["lane reports"][1]["read reports"]) == 2
    assert len(result["lane reports"][1]["read reports"][1]) == 2
    assert len(result["lane reports"][1]["read reports"][2]) == 1
    assert len(result["lane reports"][1]["other reports"]) == 0
    assert len(result["lane reports"][2]["read reports"]) == 0
    assert len(result["lane reports"][2]["other reports"]) == 1
    assert len(result["other reports"]) == 1
    assert result["run_summary"] == {
        "instrument_and_reagent_version": qc_data.instrument,
        "read_length": qc_data.read_length,
        "checkers": checker_configs,
    }

