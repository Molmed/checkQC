from collections import namedtuple
import numpy as np
import pytest


from checkQC.qc_checkers import error_rate
from checkQC.handlers.qc_handler import QCErrorFatal, QCErrorWarning

from tests.test_utils import float_eq


@pytest.fixture
def qc_data_and_exp_val():
    return (
        namedtuple("QCData", "sequencing_metrics")(
            {
                1: {
                    "reads": {
                        1: {"mean_error_rate": 0.},
                        2: {"mean_error_rate": 110.},
                        3: {"mean_error_rate": np.nan},
                    },
                },
                2: {
                    "reads": {
                        1: {"mean_error_rate": 11.},
                        2: {"mean_error_rate": 110.},
                        3: {"mean_error_rate": 9.},
                    },
                },
            }
        ),
        {
            1: {
                1: QCErrorFatal(
                    "Error rate is 0.0 on lane 1 for read 1. "
                    "This may be because no PhiX was loaded on this lane. "
                    "Use \"allow_missing_error_rate: true\" to disable this error message.",
                    data={"lane": 1, "read": 1, "error": 0.},
                ),
                2: QCErrorFatal(
                    "Error rate 110.0 > 100.0 on lane 1 for read 2.",
                    data={"lane": 1, "read": 2, "error": 110., "threshold": 100.}
                ),
                3: QCErrorFatal(
                    "Error rate is nan on lane 1 for read 3. "
                    "This may be because no PhiX was loaded on this lane. "
                    "Use \"allow_missing_error_rate: true\" to disable this error message.",
                    data={"lane": 1, "read": 3, "error": np.nan},
                ),
            },
            2: {
                1: QCErrorWarning(
                    "Error rate 11.0 > 10.0 on lane 2 for read 1.",
                    data={"lane": 2, "read": 1, "error": 11., "threshold": 10.},
                ),
                2: QCErrorFatal(
                    "Error rate 110.0 > 100.0 on lane 2 for read 2.",
                    data={"lane": 2, "read": 2, "error": 110., "threshold": 100.},
                ),
            }
        }
    )


def test_error_rate(qc_data_and_exp_val):
    qc_data, exp_val = qc_data_and_exp_val
    qc_reports = error_rate(
        qc_data,
        error_threshold=100.,
        warning_threshold=10.,
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
    qc_reports = error_rate(
        qc_data,
        error_threshold="unknown",
        warning_threshold=100.,
    )

    del exp_val[2][1]

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
    qc_reports = error_rate(
        qc_data,
        error_threshold=100.,
        warning_threshold="unknown",
    )

    del exp_val[2][1]

    assert len(qc_reports) == sum(len(v) for v in exp_val.values())
    for qc_report in qc_reports:
        lane, read = qc_report.data['lane'], qc_report.data['read']
        expected_report = exp_val[lane][read]

        assert qc_report.message == expected_report.message
        assert qc_report.type() == expected_report.type()
        for k, v in expected_report.data.items():
            assert float_eq(qc_report.data[k], v)


def test_error_rate_allow_missing(qc_data_and_exp_val):
    qc_data, exp_val = qc_data_and_exp_val
    qc_reports = error_rate(
        qc_data,
        error_threshold=100.,
        warning_threshold=10.,
        allow_missing_error_rate=True,
    )

    del exp_val[1][1]
    del exp_val[1][3]

    assert len(qc_reports) == sum(len(v) for v in exp_val.values())
    for qc_report in qc_reports:
        lane, read = qc_report.data['lane'], qc_report.data['read']
        expected_report = exp_val[lane][read]

        assert qc_report.message == expected_report.message
        assert qc_report.type() == expected_report.type()
        for k, v in expected_report.data.items():
            assert float_eq(qc_report.data[k], v)
