from collections import namedtuple
import pytest


from checkQC.qc_checkers.percent_q30 import percent_q30
from checkQC.handlers.qc_handler import QCErrorFatal, QCErrorWarning

from tests.test_utils import float_eq


@pytest.fixture
def qc_data_and_exp_val():
    return (
        namedtuple("QCData", "sequencing_metrics")(
            {
                1:{
                    "reads": {
                        1: {"percent_q30": 82., "is_index": False},
                        2: {"percent_q30": 65., "is_index": True},
                        3: {"percent_q30": 50., "is_index": True},
                        4: {"percent_q30": 80., "is_index": False},
                    },
                },
                2:{
                    "reads": {
                        1: {"percent_q30": 90., "is_index": False},
                        2: {"percent_q30": 48., "is_index": True},
                        3: {"percent_q30": 80., "is_index": False},
                        4: {"percent_q30": 64., "is_index": False},
                    },
                }

            }
        ),
        {
            1: {
                2: QCErrorWarning(
                    "%Q30 65.0 was too low on lane: 1 for read (I): 2",
                    data={"lane": 1, "read": 2, "q30": 65., "threshold": 80.},
                ),
                3: QCErrorFatal(
                    "%Q30 50.0 was too low on lane: 1 for read (I): 3",
                    data={"lane": 1, "read": 3, "q30": 50., "threshold": 60.}
                ),
            },
            2: {
                2: QCErrorFatal(
                    "%Q30 48.0 was too low on lane: 2 for read (I): 2",
                    data={"lane": 2, "read": 2, "q30": 48., "threshold": 60.},
                ),
                4: QCErrorWarning(
                    "%Q30 64.0 was too low on lane: 2 for read: 4",
                    data={"lane": 2, "read": 4, "q30": 64., "threshold": 80.},
                ),
            }
        }
    )

def test_percent_q30(qc_data_and_exp_val):
    qc_data, exp_val = qc_data_and_exp_val
    qc_reports = percent_q30(
        qc_data,
        error_threshold=60.,
        warning_threshold=80.,
    )

    assert len(qc_reports) == sum(len(v) for v in exp_val.values())
    for qc_report in qc_reports:
        lane, read = qc_report.data['lane'], qc_report.data['read']
        expected_report = exp_val[lane][read]

        assert qc_report.message == expected_report.message
        assert qc_report.type() == expected_report.type()
        for k, v in expected_report.data.items():
            assert float_eq(qc_report.data[k], v)

def test_error_rate_error_unknown(qc_data_and_exp_val):
    qc_data, exp_val = qc_data_and_exp_val
    qc_reports = percent_q30(
        qc_data,
        error_threshold="unknown",
        warning_threshold=80.,
    )

    exp_val[1][3] = QCErrorWarning(
                    "%Q30 50.0 was too low on lane: 1 for read (I): 3",
                    data={"lane": 1, "read": 3, "q30": 50., "threshold": 80.}
                )
    exp_val[2][2] = QCErrorWarning(
                    "%Q30 48.0 was too low on lane: 2 for read (I): 2",
                    data={"lane": 2, "read": 2, "q30": 48., "threshold": 80.},
                )

    assert len(qc_reports) == sum(len(v) for v in exp_val.values())
    for qc_report in qc_reports:
        lane, read = qc_report.data['lane'], qc_report.data['read']
        expected_report = exp_val[lane][read]

        assert qc_report.message == expected_report.message

        if lane != 1 or read not in [1, 3]:
            assert qc_report.type() == QCErrorWarning("").type()
        else:
            assert qc_report.type() == expected_report.type()

        for k, v in expected_report.data.items():
            assert float_eq(qc_report.data[k], v)

def test_error_rate_warning_unknown(qc_data_and_exp_val):
    qc_data, exp_val = qc_data_and_exp_val
    qc_reports = percent_q30(
        qc_data,
        error_threshold=60.,
        warning_threshold="unknown",
    )

    del exp_val[1][2]
    del exp_val[2][4]
    
    assert len(qc_reports) == sum(len(v) for v in exp_val.values())
    for qc_report in qc_reports:
        lane, read = qc_report.data['lane'], qc_report.data['read']
        expected_report = exp_val[lane][read]

        assert qc_report.message == expected_report.message
        assert qc_report.type() == expected_report.type()
        for k, v in expected_report.data.items():
            assert float_eq(qc_report.data[k], v)

