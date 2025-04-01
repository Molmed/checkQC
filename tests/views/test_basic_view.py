from collections import namedtuple

import pytest

from checkQC.views.basic import basic_view
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


def test_basic_view(qc_reports, qc_data, checker_configs):
    result = basic_view(checker_configs, qc_data, qc_reports)

    assert result == {
        'reports': [
            "Fatal QC error: ",
            "QC warning: ",
            "Fatal QC error: ",
            "Fatal QC error: ",
            "Fatal QC error: "
        ],
        'run_summary': {
            'checkers': {
                'test_checker': {
                    'error': 0,
                    'warning': 0
                }
            },
            'instrument_and_reagent_version': 'novaseq_SP',
            'read_length': 36
        },
    }

