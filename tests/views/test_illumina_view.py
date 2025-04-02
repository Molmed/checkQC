from collections import namedtuple

import pytest

from checkQC.views.illumina import illumina_view
from checkQC.handlers.qc_handler import QCErrorFatal, QCErrorWarning

@pytest.fixture
def qc_reports():
    return [
        QCErrorFatal("", data={"lane": 1, "read": 1, "qc_checker": "qc1"}),
        QCErrorWarning("", data={"lane": 1, "read": 1, "qc_checker": "qc2"}),
        QCErrorFatal("", data={"lane": 2, "qc_checker": "qc3"}),
        QCErrorFatal("", data={"lane": 1, "read": 2, "qc_checker": "qc2"}),
        QCErrorFatal("", data={"qc_checker": "qc1"}),
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

    assert result == {
        'lane reports': {
            1: {
                'qc1': ['Fatal QC error: '],
                'qc2': ['QC warning: ', 'Fatal QC error: ']
            },
            2: {
                'qc3': ['Fatal QC error: ']
            }
        },
        'other reports': {
            'qc1': ['Fatal QC error: ']
        },
        'run_summary': {
            'checkers': checker_configs,
            'instrument_and_reagent_version': qc_data.instrument,
            'read_length': qc_data.read_length,
        },
    }
