from pathlib import Path
from unittest import mock

import numpy as np
import pytest

from checkQC.qc_data import QCData
from checkQC.handlers.qc_handler import QCErrorFatal, QCErrorWarning

from tests.test_utils import float_eq


@pytest.fixture
def bclconvert_runfolder():
    parser_config = {
        "reports_location": "Reports"
    }

    return {
        "qc_data":  QCData.from_bclconvert(
            Path(__file__).parent
                / "resources/bclconvert/200624_A00834_0183_BHMTFYTINY",
            parser_config,
        ),
        "expected_instrument": "novaseq_SP",
        "expected_read_length": 36,
        "expected_samplesheet": {
            "BCLConvert_Data": {
                "len": 768,
                "head": [
                    {
                        "Lane": 1,
                        "Sample_ID": "Sample_14574-Qiagen-IndexSet1-SP-Lane1",
                        "index": "GAACTGAGCG",
                        "index2": "TCGTGGAGCG",
                    },
                    {
                        "Lane": 1,
                        "Sample_ID": "Sample_14575-Qiagen-IndexSet1-SP-Lane1",
                        "index": "AGGTCAGATA",
                        "index2": "CTACAAGATA",
                    },
                    {
                        "Lane": 1,
                        "Sample_ID": "Sample_14576-Qiagen-IndexSet1-SP-Lane1",
                        "index": "CGTCTCATAT",
                        "index2": "TATAGTAGCT",
                    },
                    {
                        "Lane": 1,
                        "Sample_ID": "Sample_14577-Qiagen-IndexSet1-SP-Lane1",
                        "index": "ATTCCATAAG",
                        "index2": "TGCCTGGTGG",
                    },
                    {
                        "Lane": 1,
                        "Sample_ID": "Sample_14578-Qiagen-IndexSet1-SP-Lane1",
                        "index": "GACGAGATTA",
                        "index2": "ACATTATCCT",
                    }
                ],
            },
        },
        "expected_sequencing_metrics": {
            1: {
                "total_cluster_pf": 532_464_327,
                "yield": 19_168_715_772,
                "yield_undetermined": 433_255_752,
                "top_unknown_barcodes": {
                    "len": 1004,
                    "head": [
                        {"index+index2": "CCTGACCACT+TAGGAGCGCA", "count": 9457},
                        {"index+index2": "AAAAAAAAAA+AAAAAAAAAA", "count": 6941},
                        {"index+index2": "GGGGGGGGGG+GAGCGCAATA", "count": 5267},
                        {"index+index2": "GCGGTGCTGC+GTCTCGTGAA", "count": 5242},
                        {"index+index2": "GGGGGGGGGG+TCGAATGGAA", "count": 4364},
                    ],
                },
                "reads": {
                    1: {
                        "mean_error_rate": np.nan,
                        "percent_q30": 95.70932006835938,
                        "is_index": False,
                        "mean_percent_phix_aligned": 0.,
                    },
                    2: {
                        "mean_error_rate": np.nan,
                        "percent_q30": 92.57965850830078,
                        "is_index": True,
                        "mean_percent_phix_aligned": np.nan,
                    },
                    3: {
                        "mean_error_rate": np.nan,
                        "percent_q30": 90.3790283203125,
                        "is_index": True,
                        "mean_percent_phix_aligned": np.nan,
                    },
                },
            },
            2: {
                "total_cluster_pf": 530_917_565,
                "yield": 19_113_032_340,
                "yield_undetermined": 426_560_256,
                "top_unknown_barcodes": {
                    "len": 1000,
                    "head": [
                        {"index+index2": "CCTGACCACT+TAGGAGCGCA", "count": 9191},
                        {"index+index2": "AAAAAAAAAA+AAAAAAAAAA", "count": 8182},
                        {"index+index2": "GGGGGGGGGG+GAGCGCAATA", "count": 5081},
                        {"index+index2": "GGGGGGGGGG+CACGGATTAT", "count": 4348},
                        {"index+index2": "GGGGGGGGGG+TCGAATGGAA", "count": 4290},
                    ],
                },
                "reads": {
                    1: {
                        "mean_error_rate": np.nan,
                        "percent_q30": 95.75276184082031,
                        "is_index": False,
                        "mean_percent_phix_aligned": 0.,
                    },
                    2: {
                        "mean_error_rate": np.nan,
                        "percent_q30": 92.60448455810547,
                        "is_index": True,
                        "mean_percent_phix_aligned": np.nan,
                    },
                    3: {
                        "mean_error_rate": np.nan,
                        "percent_q30": 90.2811050415039,
                        "is_index": True,
                        "mean_percent_phix_aligned": np.nan,
                    },
                },
            },
        },
    }


def test_qc_data(bclconvert_runfolder):
    qc_data = bclconvert_runfolder["qc_data"]
    expected_sequencing_metrics = bclconvert_runfolder["expected_sequencing_metrics"]

    assert qc_data.instrument == bclconvert_runfolder["expected_instrument"]
    assert qc_data.read_length == bclconvert_runfolder["expected_read_length"]

    assert (
        len(qc_data.samplesheet["BCLConvert_Data"])
        == bclconvert_runfolder["expected_samplesheet"]["BCLConvert_Data"]["len"]
    )
    assert (
        qc_data.samplesheet["BCLConvert_Data"][:5]
        == bclconvert_runfolder["expected_samplesheet"]["BCLConvert_Data"]["head"]
    )

    for lane, lane_data in expected_sequencing_metrics.items():
        for lane_metric, lane_metric_value in lane_data.items():
            match lane_metric:
                case "top_unknown_barcodes":
                    assert len(qc_data.sequencing_metrics[lane][lane_metric]) == lane_metric_value["len"]
                    assert qc_data.sequencing_metrics[lane][lane_metric][:5] == lane_metric_value["head"]
                case "reads":
                    for read, read_data in lane_metric_value.items():
                        for read_metric, read_metric_value in read_data.items():
                            actual_value = qc_data.sequencing_metrics[lane]["reads"][read][read_metric]
                            if type(read_metric_value) == float:
                                assert float_eq(read_metric_value, actual_value)
                            else:
                                assert read_metric_value == actual_value
                case _:
                    assert qc_data.sequencing_metrics[lane][lane_metric] == lane_metric_value


@pytest.fixture
def checker_configs():
    return {
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


def test_report(bclconvert_runfolder, checker_configs):
    mock_qc_error = QCErrorFatal("Mock error message")

    qc_data = bclconvert_runfolder["qc_data"]
    qc_data.mock_checker = lambda self, error, warning: [mock_qc_error]
    qc_data.mock_view = lambda self, qc_reports: qc_reports

    reports = qc_data.report(checker_configs)

    assert len(reports) == 1
    assert str(reports[0]) == str(mock_qc_error)


def test_report_default_checker(bclconvert_runfolder, checker_configs):
    checker_configs["default_handlers"] = [
        {"name": "mock_checker", "error": 2, "warning": 1},
        {"name": "mock_checker_bis", "error": 0, "warning": 1},
    ]

    qc_data = bclconvert_runfolder["qc_data"]
    qc_data.mock_checker = lambda self, error, warning: [QCErrorFatal(f"error={error}")]
    qc_data.mock_checker_bis = lambda self, error, warning: [QCErrorFatal(f"error_bis={error}")]
    qc_data.mock_view = lambda self, qc_reports: qc_reports

    reports = qc_data.report(checker_configs)

    assert len(reports) == 2
    assert any("error=5" in str(report) for report in reports)
    assert any("error_bis=0" in str(report) for report in reports)


def test_report_range_read_len(bclconvert_runfolder, checker_configs):
    qc_data = bclconvert_runfolder["qc_data"]
    qc_data.read_length = 38
    qc_data.mock_checker = lambda self, error, warning: [QCErrorFatal(f"error={error}")]
    qc_data.mock_view = lambda self, qc_reports: qc_reports

    reports = qc_data.report(checker_configs)

    assert len(reports) == 1
    assert "error=6" in str(reports[0])


def test_report_use_closest_read_len(bclconvert_runfolder, checker_configs):
    qc_data = bclconvert_runfolder["qc_data"]
    qc_data.read_length = 35
    qc_data.mock_checker = lambda self, error, warning: [QCErrorFatal(f"error={error}")]
    qc_data.mock_view = lambda self, qc_reports: qc_reports

    with pytest.raises(KeyError):
        reports = qc_data.report(checker_configs)

    reports = qc_data.report(checker_configs, use_closest_read_len=True)

    assert len(reports) == 1
    assert "error=5" in str(reports[0])
