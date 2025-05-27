import json
from pathlib import Path

import click
from click.testing import CliRunner
import pytest

from checkQC.app import start


@pytest.fixture
def runfolder_data():
    runfolder_path = str(Path(__file__).parent / "resources/bclconvert/200624_A00834_0183_BHMTFYTINY/")
    expected_data = (Path(runfolder_path) / "expected_qc.json").read_text()

    return runfolder_path, expected_data


def test_checkqc(runfolder_data):
    runfolder_path, expected_data = runfolder_data
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(
        start,
        [
            "--config", "checkQC/default_config/config.yaml",
            "--json",
            "--demultiplexer", "bclconvert",
            "--use-closest-read-length",
            runfolder_path,
        ],
    )

    assert result.exit_code == 1
    assert result.output == expected_data


def test_checkqc_default_config(runfolder_data):
    runfolder_path, expected_data = runfolder_data
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(
        start,
        [
            "--json",
            "--demultiplexer", "bclconvert",
            "--use-closest-read-length",
            runfolder_path,
        ],
    )

    assert result.exit_code == 1
    assert result.output == expected_data
