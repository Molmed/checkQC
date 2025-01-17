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

def test_illumima_view(qc_reports):
    result = illumina_view(None, qc_reports)

    assert len(result["lane reports"]) == 2
    assert len(result["lane reports"][1]["read reports"]) == 2
    assert len(result["lane reports"][1]["read reports"][1]) == 2
    assert len(result["lane reports"][1]["read reports"][2]) == 1
    assert len(result["lane reports"][1]["other reports"]) == 0
    assert len(result["lane reports"][2]["read reports"]) == 0
    assert len(result["lane reports"][2]["other reports"]) == 1
    assert len(result["other reports"]) == 1

