from pathlib import Path

import pytest

from checkQC.app import App
from checkQC.app import run_new_checkqc


@pytest.fixture
def bcl2fastq_runfolder_path():
    return str(Path(__file__).parent / "resources/bcl2fastq/170726_D00118_0303_BCB1TVANXX/")


@pytest.fixture
def bclconvert_runfolder_path():
    return str(Path(__file__).parent / "resources/bclconvert/200624_A00834_0183_BHMTFYTINY/")


def test_run(bcl2fastq_runfolder_path):
    app = App(runfolder=bcl2fastq_runfolder_path)
    # The test data contains fatal qc errors
    assert app.run() == 1


def test_run_json_mode(bcl2fastq_runfolder_path):
    app = App(runfolder=bcl2fastq_runfolder_path, json_mode=True)
    # The test data contains fatal qc errors
    assert app.run() == 1


def test_run_use_closest_read_length(bcl2fastq_runfolder_path):
    config_file = Path("tests") / "resources/read_length_not_in_config.yaml"
    app = App(
        runfolder=bcl2fastq_runfolder_path,
        config_file=config_file,
        use_closest_read_length=True,
    )
    # The test data contains fatal qc errors
    assert app.run() == 1


def test_run_downgrade_error(bcl2fastq_runfolder_path):
    app = App(
        runfolder=bcl2fastq_runfolder_path,
        downgrade_errors_for="ReadsPerSampleHandler",
    )
    # Test data should not produce fatal qc errors anymore
    assert app.run() == 0


def test_run_new_checkqc(bclconvert_runfolder_path):
    exit_status, reports = run_new_checkqc(
        None,
        bclconvert_runfolder_path,
        downgrade_errors_for="ReadsPerSampleHandler",
        use_closest_read_length=True,
        demultiplexer="bclconvert",
    )

    expected_data = (
        Path(bclconvert_runfolder_path) / "expected_qc.json").read_text()

    assert exit_status == 1
    assert reports + '\n' == expected_data
