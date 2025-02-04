from collections import namedtuple
import pytest

from checkQC.qc_checkers import reads_per_sample
from checkQC.handlers.qc_handler import QCErrorFatal, QCErrorWarning


@pytest.fixture
def qc_data_and_exp_val():
    return (
        namedtuple("QCData", "sequencing_metrics")(
            {
                1: {
                    "reads_per_sample": [
                        {
                            "sample_id": "Sample_A",
                            "cluster_count": 100_000_000
                            },
                        {
                            "sample_id": "Sample_B",
                            "cluster_count": 20_000_000
                            },
                    ],
                },
                2: {
                    "reads_per_sample": [
                        {
                            "sample_id": "Sample_C",
                            "cluster_count": 29_000_000
                            },
                        {
                            "sample_id": "Sample_D",
                            "cluster_count": 60_000_000
                            },
                    ],
                },
            }
        ),
        {
            1:
                QCErrorFatal(
                    "Number of reads for sample Sample_B on lane 1 were too low:"
                    " 20.0 M (threshold: 25.0 M)",
                    data={"lane": 1,
                          "number_of_samples": 2,
                          "sample_id": "Sample_B",
                          "sample_reads": 20,
                          "threshold": 25}
                ),
            2:
                QCErrorWarning(
                    "Number of reads for sample Sample_C on lane 2 were too low:"
                    " 29.0 M (threshold: 30.0 M)",
                    data={"lane": 2,
                          "number_of_samples": 2,
                          "sample_id": "Sample_C",
                          "sample_reads": 29,
                          "threshold": 30}
                ),
        }
    )


def test_reads_per_sample(qc_data_and_exp_val):
    qc_data, exp_val = qc_data_and_exp_val
    qc_reports = reads_per_sample(
        qc_data,
        error_threshold=50,
        warning_threshold=60,
    )

    assert len(qc_reports) == 4
    for qc_report in filter(None, qc_reports):
        lane = qc_report.data['lane']
        expected_report = exp_val[lane]

        assert qc_report.message == expected_report.message
        assert qc_report.type() == expected_report.type()
        for k, v in expected_report.data.items():
            assert qc_report.data[k] == v


def test_reads_per_sample_unknown_threshold(qc_data_and_exp_val):
    qc_data, exp_val = qc_data_and_exp_val
    qc_reports = reads_per_sample(
        qc_data,
        error_threshold="unknown",
        warning_threshold=60,
    )

    assert len(qc_reports) == 4
    expected_report = QCErrorWarning(
                "Number of reads for sample Sample_B on lane 1 were too low:"
                " 20.0 M (threshold: 30.0 M)",
                data={"lane": 1,
                      "number_of_samples": 2,
                      "sample_id": "Sample_B",
                      "sample_reads": 20,
                      "threshold": 30}
                )
    assert qc_reports[1].type() == expected_report.type()
    assert qc_reports[1].data == expected_report.data
