from pathlib import Path

import pytest

from checkQC.app import App


@pytest.fixture
def runfolder_path():
    return str(Path(__file__).parent / "resources/170726_D00118_0303_BCB1TVANXX/")


def test_run(runfolder_path):
    app = App(runfolder=runfolder_path)
    # The test data contains fatal qc errors
    assert app.run() == 1


def test_run_json_mode(runfolder_path):
    app = App(runfolder=runfolder_path, json_mode=True)
    # The test data contains fatal qc errors
    assert app.run() == 1


def test_run_use_closest_read_length(runfolder_path):
    config_file = Path("tests") / "resources/read_length_not_in_config.yaml"
    app = App(
        runfolder=runfolder_path,
        config_file=config_file,
        use_closest_read_length=True,
    )
    # The test data contains fatal qc errors
    assert app.run() == 1


def test_run_downgrade_error(runfolder_path):
    app = App(
        runfolder=runfolder_path,
        downgrade_errors_for="ReadsPerSampleHandler",
    )
    # Test data should not produce fatal qc errors anymore
    assert app.run() == 0
