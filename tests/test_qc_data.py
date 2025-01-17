from pathlib import Path

import numpy as np
import pytest

from checkQC.qc_data import QCData

from tests.test_utils import float_eq


@pytest.fixture
def bclconvert_runfolder():
    return {
        "path":  Path(__file__).parent / "resources/bclconvert/200624_A00834_0183_BHMTFYTINY",
        "expected_instrument": "novaseq_SP",
        "expected_read_length": 36,
        "expected_samplesheet": {
            "BCLConvert_Data": {
                "len": 4,
                "head": [
                    {
                        "Lane": 1,
                        "Sample_ID": "Sample_14574-Qiagen-IndexSet1-SP-Lane1",
                        "Index": "GAACTGAGCG",
                        "Index2": "TCGTGGAGCG",
                        "Sample_Project": "AB-1234",
                    },
                    {
                        "Lane": 1,
                        "Sample_ID": "Sample_14575-Qiagen-IndexSet1-SP-Lane1",
                        "Index": "AGGTCAGATA",
                        "Index2": "CTACAAGATA",
                        "Sample_Project": "CD-5678",
                    },
                    {
                        "Lane": 2,
                        "Sample_ID": "Sample_14574-Qiagen-IndexSet1-SP-Lane2",
                        "Index": "GAACTGAGCG",
                        "Index2": "TCGTGGAGCG",
                        "Sample_Project": "AB-1234",
                    },
                    {
                        "Lane": 2,
                        "Sample_ID": "Sample_14575-Qiagen-IndexSet1-SP-Lane2",
                        "Index": "AGGTCAGATA",
                        "Index2": "CTACAAGATA",
                        "Sample_Project": "CD-5678",
                    },
                ],
            },
        },
        "expected_sequencing_metrics": {
            1: {
                "total_cluster_pf": 532_464_327,
                "yield": 122_605_416,
                "yield_undetermined": 121_940_136,
                "top_unknown_barcodes": {
                    "len": 1029,
                    "head": [
                        {"index+index2": "ATATCTGCTT+TAGACAATCT", "count": 12857},
                        {"index+index2": "CACCTCTCTT+CTCGACTCCT", "count": 12406},
                        {"index+index2": "ATGTAACGTT+ACGATTGCTG", "count": 12177},
                        {"index+index2": "TTCGGTGTGA+GAACAAGTAT", "count": 11590},
                        {"index+index2": "GGTCCGCTTC+CTCACACAAG", "count": 11509},
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
                "reads_per_sample": [
                    {
                        "sample_id": "Sample_14574-Qiagen-IndexSet1-SP-Lane1",
                        "cluster_count": 9920,
                        "fraction_mapped": 0.0019000000320374966,
                    },
                    {
                        "sample_id": "Sample_14575-Qiagen-IndexSet1-SP-Lane1",
                        "cluster_count": 8560,
                        "fraction_mapped": 0.0015999999595806003,
                    },
                ],
            },
            2: {
                "total_cluster_pf": 530_917_565,
                "yield": 124_497_108,
                "yield_undetermined": 123_817_428,
                "top_unknown_barcodes": {
                    "len": 1055,
                    "head": [
                        {"index+index2": "ATATCTGCTT+TAGACAATCT", "count": 13176},
                        {"index+index2": "ATGTAACGTT+ACGATTGCTG", "count": 12395},
                        {"index+index2": "CACCTCTCTT+CTCGACTCCT", "count": 12247},
                        {"index+index2": "TTCGGTGTGA+GAACAAGTAT", "count": 11909},
                        {"index+index2": "TAATTAGCGT+TGGTTAAGAA", "count": 11330},
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
                "reads_per_sample": [
                    {
                        "sample_id": "Sample_14574-Qiagen-IndexSet1-SP-Lane2",
                        "cluster_count": 10208,
                        "fraction_mapped": 0.0019000000320374966,
                    },
                    {
                        "sample_id": "Sample_14575-Qiagen-IndexSet1-SP-Lane2",
                        "cluster_count": 8672,
                        "fraction_mapped": 0.0015999999595806003,
                    },
                ],
            },
        },
    }

def test_qc_data(bclconvert_runfolder):
    runfolder_path = bclconvert_runfolder["path"]
    expected_sequencing_metrics = bclconvert_runfolder["expected_sequencing_metrics"]

    parser_config = {
        "reports_location": "Reports"
    }

    qc_data = QCData.from_bclconvert(runfolder_path, parser_config)

    assert qc_data.instrument == bclconvert_runfolder["expected_instrument"]
    assert qc_data.read_length == bclconvert_runfolder["expected_read_length"]

    assert (
        len(qc_data.samplesheet["BCLConvert_Data"])
        == bclconvert_runfolder["expected_samplesheet"]["BCLConvert_Data"]["len"]
    )
    assert (
        qc_data.samplesheet["BCLConvert_Data"]
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
