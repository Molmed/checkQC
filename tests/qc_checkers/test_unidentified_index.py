from collections import namedtuple

from checkQC.qc_checkers.unidentified_index import unidentified_index, SamplesheetMatcher

import pytest

@pytest.fixture
def samplesheet_matcher():
    return SamplesheetMatcher([
        {"Index": "CCAA", "Index2": "AGCA", "Lane": 1, "Sample_ID": "dual reverse"},
        {"Index": "GGTT", "Index2": "TCGT", "Lane": 2, "Sample_ID": "dual reverse complement"},
        {"Index": "TGCT", "Index2": "TTGG", "Lane": 3, "Sample_ID": "dual complement"},
        {"Index": "AAAT", "Index2": "ATAT", "Lane": 1, "Sample_ID": "sample_id"},
        {"Index": "CAAT", "Index2": "CTAT", "Lane": 1, "Sample_ID": "sample_id"},
        {"Index": "TCCA", "Index2": "", "Lane": 1, "Sample_ID": "reverse"},
        {"Index": "AGGT", "Index2": "", "Lane": 1, "Sample_ID": "reverse complement"},
        {"Index": "TGGA", "Index2": "", "Lane": 1, "Sample_ID": "complement"},
    ])


# TODO print message with break point and add to tests
def test_check_complement_and_reverse(samplesheet_matcher):
    barcode = {
        "index": "ACGA",
        "index2": "AACC",
        "lane": 1,
    }

    # OBS: samplesheet rows are reported twice because it matches both indices
    causes = samplesheet_matcher.check_complement_and_reverse(barcode)
    assert len(causes) == 6
    assert any(data[0] == "reverse" for _, data in causes)
    assert any(data[0] == "complement" for _, data in causes)
    assert any(data[0] == "reverse complement" for _, data in causes)
    assert all(data[1]["Sample_ID"].startswith("dual") for _, data in causes)
    assert all(data[1]["Sample_ID"].startswith("dual") for _, data in causes)
    assert all(data[1]["Sample_ID"].startswith("dual") for _, data in causes)

    barcode = {
        "index": "ACGT",
        "lane": 1,
    }
    causes = samplesheet_matcher.check_complement_and_reverse(barcode)
    assert len(causes) == 0


def test_check_complement_and_reverse_single_indices(samplesheet_matcher):
    barcode = {
        "index": "ACCT",
        "lane": 1,
    }
    causes = samplesheet_matcher.check_complement_and_reverse(barcode)
    assert len(causes) == 3
    assert any(data[0] == "reverse" for _, data in causes)
    assert any(data[0] == "complement" for _, data in causes)
    assert any(data[0] == "reverse complement" for _, data in causes)

    barcode = {
        "index": "ACCT",
        "index2": "CCCC",
        "lane": 1,
    }
    causes = samplesheet_matcher.check_complement_and_reverse(barcode)
    assert len(causes) == 0

def test_lane_swap(samplesheet_matcher):
    barcode = {
        "index": "CCAA",
        "index2": "AGCA",
        "lane": 1,
    }
    causes = samplesheet_matcher.check_lane_swap(barcode)
    assert len(causes) == 0

    barcode["lane"] = 2
    causes = samplesheet_matcher.check_lane_swap(barcode)
    assert len(causes) == 1
    assert causes[0][1][0] == "lane swap"


def test_dual_index_swap(samplesheet_matcher):
    barcode = {
        "index": "AGCA",
        "index2": "CCAA",
        "lane": 1,
    }
    causes = samplesheet_matcher.check_dual_index_swap(barcode)
    assert len(causes) == 1
    assert causes[0][1][0] == "dual index swap"


@pytest.fixture
def qc_data():
    return namedtuple("QCData", ["sequencing_metrics", "samplesheet"])(
        {
            1: {
                "total_cluster_pf": 100,
                "top_unknown_barcodes": [
                    { "lane": 1, "index": "ACCT", "count": 10 },
                ],
            }
        },
        [
            {"Index": "ACCT", "Lane": 2, "Sample_ID": "lane swap"},
            {"Index": "TCCA", "Lane": 1, "Sample_ID": "reverse"},
        ]
    )


def test_unidentified_index(qc_data):
    reports = unidentified_index(qc_data, 5.)

    assert len(reports) == 1
    assert str(reports[0]) == """QC warning: Overrepresented unknown barcode: ACCT (10.0% > 5.0%).
Possible causes are:
- reverse index "TCCA" found in samplesheet for sample reverse, lane 1
- index ACCT found on lane 2"""


def test_whitelist_index(qc_data):
    reports = unidentified_index(
            qc_data, 5.,
            white_listed_indexes=[".*AC.*"])
    assert len(reports) == 1
    assert str(reports[0]) == (
        "QC warning: Overrepresented unknown barcode: ACCT (10.0% > 5.0%). "
        "This barcode is white-listed."
    )
