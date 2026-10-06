from collections import namedtuple

from checkQC.qc_checkers.unidentified_index import unidentified_index, SamplesheetMatcher

import pytest

@pytest.fixture
def samplesheet_matcher():
    return SamplesheetMatcher([
        {"index": "CCAA", "index2": "AGCA", "lane": 1, "sample_id": "dual reverse"},
        {"index": "GGTT", "index2": "TCGT", "lane": 2, "sample_id": "dual reverse complement"},
        {"index": "TGCT", "index2": "TTGG", "lane": 3, "sample_id": "dual complement"},
        {"index": "AAAT", "index2": "ATAT", "lane": 1, "sample_id": "sample_id"},
        {"index": "CAAT", "index2": "CTAT", "lane": 1, "sample_id": "sample_id"},
        {"index": "TCCA", "index2": "", "lane": 1, "sample_id": "reverse"},
        {"index": "AGGT", "index2": "", "lane": 1, "sample_id": "reverse complement"},
        {"index": "TGGA", "index2": "", "lane": 1, "sample_id": "complement"},
        {"index": "AAGG", "index2": "", "lane": 1, "sample_id": "test"},
    ])



def test_check_complement(samplesheet_matcher):
    barcode_data = {
        "barcode": {"index": "TTCC", "index2": ""},
        "lane": 1,
    }

    causes = samplesheet_matcher.check_complement_and_reverse(barcode_data)

    assert len(causes) == 1

    msg, data = causes[0]

    assert msg == "complement index swap: \"AAGG\" found in samplesheet for sample \"test\", lane 1"
    print(data)
    assert data == (
        "complement",
        {"index": "AAGG", "index2": "", "lane": 1, "sample_id": "test"}
    )


def test_check_reverse(samplesheet_matcher):
    barcode_data = {
        "barcode": {"index": "GGAA", "index2": ""},
        "lane": 1,
    }
    causes = samplesheet_matcher.check_complement_and_reverse(barcode_data)

    assert len(causes) == 1

    msg, data = causes[0]

    assert msg == "reverse index swap: \"AAGG\" found in samplesheet for sample \"test\", lane 1"
    assert data == (
        "reverse",
        {"index": "AAGG", "index2": "", "lane": 1, "sample_id": "test"}
    )


def test_check_reverse_complement(samplesheet_matcher):
    barcode_data = {
        "barcode": {"index": "CCTT", "index2": ""},
        "lane": 1,
    }
    causes = samplesheet_matcher.check_complement_and_reverse(barcode_data)

    assert len(causes) == 1

    msg, data = causes[0]

    assert msg == "reverse complement index swap: \"AAGG\" found in samplesheet for sample \"test\", lane 1"
    assert data == (
        "reverse complement",
        {"index": "AAGG", "index2": "", "lane": 1, "sample_id": "test"}
    )


def test_check_complement_and_reverse(samplesheet_matcher):
    barcode_data = {
        "barcode": {"index": "ACGA", "index2": "AACC"},
        "lane": 1,
    }

    # NOTE: samplesheet rows are reported twice because it matches both indices
    causes = samplesheet_matcher.check_complement_and_reverse(barcode_data)
    assert len(causes) == 6
    assert any(data[0] == "reverse" for _, data in causes)
    assert any(data[0] == "complement" for _, data in causes)
    assert any(data[0] == "reverse complement" for _, data in causes)
    assert all(data[1]["sample_id"].startswith("dual") for _, data in causes)

    barcode_data = {
        "barcode": {"index": "ACGT"},
        "lane": 1,
    }
    causes = samplesheet_matcher.check_complement_and_reverse(barcode_data)
    assert len(causes) == 0


def test_check_complement_and_reverse_single_indices(samplesheet_matcher):
    barcode_data = {
        "barcode": {"index": "ACCT"},
        "lane": 1,
    }
    causes = samplesheet_matcher.check_complement_and_reverse(barcode_data)
    assert len(causes) == 3
    assert any(data[0] == "reverse" for _, data in causes)
    assert any(data[0] == "complement" for _, data in causes)
    assert any(data[0] == "reverse complement" for _, data in causes)

    barcode_data = {
        "barcode": {"index": "ACCT", "index2": "CCCC"},
        "lane": 1,
    }
    causes = samplesheet_matcher.check_complement_and_reverse(barcode_data)
    assert len(causes) == 0


def test_lane_swap(samplesheet_matcher):
    barcode_data = {
        "barcode": {"index": "CCAA", "index2": "AGCA"},
        "lane": 1,
    }
    causes = samplesheet_matcher.check_lane_swap(barcode_data)
    assert len(causes) == 0

    barcode_data["lane"] = 2
    causes = samplesheet_matcher.check_lane_swap(barcode_data)
    assert len(causes) == 1
    msg, data = causes[0]
    assert msg == "lane swap: index \"CCAA+AGCA\" found in samplesheet for sample \"dual reverse\", lane 1"
    assert data == (
        "lane swap",
        {
            "index": "CCAA",
            "index2": "AGCA",
            "lane": 1,
            "sample_id": "dual reverse",
        }
    )


def test_dual_index_swap(samplesheet_matcher):
    barcode_data = {
        "barcode": {"index": "AGCA", "index2": "CCAA"},
        "lane": 1,
    }
    causes = samplesheet_matcher.check_dual_index_swap(barcode_data)
    assert len(causes) == 1
    msg, data = causes[0]
    assert msg == "dual index swap: barcode \"CCAA+AGCA\" found in samplesheet for sample \"dual reverse\", lane 1"
    assert data == (
        "dual index swap",
        {
            "index": "CCAA",
            "index2": "AGCA",
            "lane": 1,
            "sample_id": "dual reverse",
        }
    )


@pytest.fixture
def qc_data():
    return namedtuple("QCData", ["sequencing_metrics", "samplesheet"])(
        {
            1: {
                "total_reads_pf": 100,
                "top_unknown_barcodes": [
                    {"lane": 1, "index": "ACCT", "count": 10},
                    {"lane": 1, "index": "AC", "count": 50},
                ],
            }
        },
        [
            {"index": "ACCT", "lane": 2, "sample_id": "lane swap"},
            {"index": "TCCA", "lane": 1, "sample_id": "reverse"},
        ]
    )


def test_unidentified_index(qc_data):
    reports = unidentified_index(qc_data, 5.)

    assert len(reports) == 2
    assert None not in reports
    assert str(reports[0]) == """Fatal QC error: Overrepresented unknown barcode "ACCT" on lane 1 (10.0% > 5.0%).
Possible causes are:
- reverse index swap: "TCCA" found in samplesheet for sample "reverse", lane 1
- lane swap: index "ACCT" found in samplesheet for sample "lane swap", lane 2"""
    assert reports[0].type() == "error"
    assert reports[0].data == {
        "barcode": {
            "count": 10,
            "index": "ACCT",
            "lane": 1,
        },
        "causes": [
            ("reverse", {"index": "TCCA", "lane": 1, "sample_id": "reverse"}),
            ("lane swap", {"index": "ACCT", "lane": 2, "sample_id": "lane swap"}),
        ],
        "is_white_listed": False,
        "lane": 1,
        "significance": 10.0,
        "threshold": 5.0,
        "qc_checker": "unidentified_index",
    }
    assert str(reports[1]) == "Fatal QC error: Overrepresented unknown barcode \"AC\" on lane 1 (50.0% > 5.0%)."
    assert reports[1].type() == "error"


def test_whitelist_index(qc_data):
    reports = unidentified_index(
            qc_data, 5.,
            white_listed_indexes=[".*CC.*"])
    assert len(reports) == 2
    assert None not in reports
    assert str(reports[0]).startswith(
        "QC warning: Overrepresented unknown barcode \"ACCT\" on lane 1 (10.0% > 5.0%). "
        "This barcode is white-listed."
    )
    assert reports[0].type() == "warning"
