from pathlib import Path
import pytest

from checkQC.qc_data_utils import bclconvert_test_runfolder
from checkQC.qc_data import QCData

from tests.test_utils import float_eq


@pytest.fixture
def bclconvert_runfolder():
    parser_config = {
        "reports_location": "Reports"
    }

    qc_data = QCData.from_bclconvert(
        Path(__file__).parent / "resources/bclconvert/200624_A00834_0183_BHMTFYTINY",
        parser_config,
    )
    return bclconvert_test_runfolder(qc_data)



def test_qc_data(bclconvert_runfolder):
    qc_data = bclconvert_runfolder["qc_data"]
    expected_sequencing_metrics = bclconvert_runfolder["expected_sequencing_metrics"]

    assert qc_data.instrument == bclconvert_runfolder["expected_instrument"]
    assert qc_data.read_length == bclconvert_runfolder["expected_read_length"]

    assert (
        len(qc_data.samplesheet)
        == bclconvert_runfolder["expected_samplesheet"]["len"]
    )
    assert (
        qc_data.samplesheet
        == bclconvert_runfolder["expected_samplesheet"]["head"]
    )

    for lane, expected_lane_data in expected_sequencing_metrics.items():
        for lane_metric, expected_lane_metric_value in expected_lane_data.items():
            lane_data = qc_data.sequencing_metrics[lane]
            match lane_metric:
                case "top_unknown_barcodes":
                    assert len(lane_data[lane_metric]) == expected_lane_metric_value["len"]
                    assert lane_data[lane_metric][:5] == expected_lane_metric_value["head"]
                case "reads":
                    for read, expected_read_data in expected_lane_metric_value.items():
                        for read_metric, expected_read_metric_value in expected_read_data.items():
                            read_metric_value = lane_data["reads"][read][read_metric]
                            if type(expected_read_metric_value) == float:
                                assert float_eq(expected_read_metric_value, read_metric_value)
                            else:
                                assert expected_read_metric_value == read_metric_value
                case _:
                    assert lane_data[lane_metric] == expected_lane_metric_value
