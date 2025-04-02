from pathlib import Path

import pytest

from checkQC.parsers.illumina import (
    _read_interop_summary,
    _read_quality_metrics,
    _read_top_unknown_barcodes,
    _read_run_metadata,
    _read_samplesheet,
)


@pytest.fixture
def runfolder_path():
    return (
        Path(__file__).parent.parent
        / "resources/bclconvert/200624_A00834_0183_BHMTFYTINY"
    )


def test_read_interop_summary(runfolder_path):
    run_summary, index_summary = _read_interop_summary(runfolder_path)

    total_cluster_pf = run_summary.at(0).at(0).reads_pf()
    assert total_cluster_pf == 532464327

    sample_id = index_summary.at(0).at(0).sample_id()
    assert sample_id == "Sample_14574-Qiagen-IndexSet1-SP-Lane1"


def test_read_quality_metrics(runfolder_path):
    quality_metrics = _read_quality_metrics(
            runfolder_path / "Reports/Quality_Metrics.csv")

    assert len(quality_metrics) == 6
    assert quality_metrics[0] == {
        '% Q30': '0.96',
        'Lane': '1',
        'Mean Quality Score (PF)': '36.37',
        'QualityScoreSum': '12987964',
        'ReadNumber': '1',
        'SampleID': 'Sample_14574-Qiagen-IndexSet1-SP-Lane1',
        'Sample_Project': 'AB-1234',
        'Yield': '357120',
        'YieldQ30': '342989',
        'index': 'GAACTGAGCG',
        'index2': 'TCGTGGAGCG',
    }


def test_read_to_unknown_barcodes(runfolder_path):
    top_unknown_barcodes = _read_top_unknown_barcodes(
            runfolder_path / "Reports/Top_Unknown_Barcodes.csv")

    assert len(top_unknown_barcodes) == 2084
    assert top_unknown_barcodes[:3] == [
        {
            '# Reads': '12857',
            '% of All Reads': '0.003775',
            '% of Unknown Barcodes': '0.003796',
            'Lane': '1',
            'index': 'ATATCTGCTT',
            'index2': 'TAGACAATCT',
        },
        {
            '# Reads': '12406',
            '% of All Reads': '0.003643',
            '% of Unknown Barcodes': '0.003663',
            'Lane': '1',
            'index': 'CACCTCTCTT',
            'index2': 'CTCGACTCCT',
        },
        {
            '# Reads': '12177',
            '% of All Reads': '0.003575',
            '% of Unknown Barcodes': '0.003595',
            'Lane': '1',
            'index': 'ATGTAACGTT',
            'index2': 'ACGATTGCTG',
        },
    ]


# TODO add tests with paired end reads
def test_read_run_metadata(runfolder_path):
    instrument, read_length = _read_run_metadata(runfolder_path)
    assert instrument == "novaseq_SP"
    assert read_length == 36


def test_read_samplesheet(runfolder_path):
    samplesheet = _read_samplesheet(runfolder_path)

    assert len(samplesheet) == 4
    assert all(
        key.lower() == key
        for row in samplesheet
        for key in row
    )
    assert all(
        " " not in row["index"] and " " not in row["index2"]
        for row in samplesheet
    )
    assert samplesheet[0] == {
        'index': 'GAACTGAGCG',
        'index2': 'TCGTGGAGCG',
        'lane': 1,
        'sample_id': 'Sample_14574-Qiagen-IndexSet1-SP-Lane1',
        'sample_project': 'AB-1234',
    }
