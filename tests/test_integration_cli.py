import json
from pathlib import Path

import click
from click.testing import CliRunner
import pytest

from checkQC.app import start


@pytest.fixture
def runfolder_data():
    runfolder_path = str(Path(__file__).parent / "resources/bclconvert/200624_A00834_0183_BHMTFYTINY/")
    expected_data = {
        "lane reports": {
            "1": {
                "error_rate": [
                    "Fatal QC error: Error rate is nan on lane 1 for read 1. This may be because no PhiX was loaded on this lane. Use \"allow_missing_error_rate: true\" to disable this error message."
                ],
                "reads_per_sample": [
                    "Fatal QC error: Number of reads for sample Sample_14574-Qiagen-IndexSet1-SP-Lane1 on lane 1 were too low: 0.00992 M (threshold: 121.875 M)",
                    "Fatal QC error: Number of reads for sample Sample_14575-Qiagen-IndexSet1-SP-Lane1 on lane 1 were too low: 0.00856 M (threshold: 121.875 M)"
                ],
                "undetermined_percentage": [
                    "Fatal QC error: Percentage of undetermined indices 99.46% (- 0.00% phiX) > 9.00% on lane 1."
                ]
            },
            "2": {
                "error_rate": [
                    "Fatal QC error: Error rate is nan on lane 2 for read 1. This may be because no PhiX was loaded on this lane. Use \"allow_missing_error_rate: true\" to disable this error message."
                ],
                "reads_per_sample": [
                    "Fatal QC error: Number of reads for sample Sample_14574-Qiagen-IndexSet1-SP-Lane2 on lane 2 were too low: 0.010208 M (threshold: 121.875 M)",
                    "Fatal QC error: Number of reads for sample Sample_14575-Qiagen-IndexSet1-SP-Lane2 on lane 2 were too low: 0.008672 M (threshold: 121.875 M)"
                ],
                "undetermined_percentage": [
                    "Fatal QC error: Percentage of undetermined indices 99.45% (- 0.00% phiX) > 9.00% on lane 2."
                ]
            }
        },
        "run_summary": {
            "instrument_and_reagent_version": "novaseq_SP",
            "read_length": 36,
            "checkers": {
                "UndeterminedPercentageHandler": {
                    "warning_threshold": "unknown",
                    "error_threshold": 9
                },
                "UnidentifiedIndexHandler": {
                    "significance_threshold": 1,
                    "white_listed_indexes": [
                        ".*N.*",
                        "G{6,}"
                    ]
                },
                "ClusterPFHandler": {
                    "warning_threshold": 325,
                    "error_threshold": "unknown"
                },
                "Q30Handler": {
                    "warning_threshold": 90,
                    "error_threshold": "unknown"
                },
                "ErrorRateHandler": {
                    "allow_missing_error_rate": False,
                    "warning_threshold": 1,
                    "error_threshold": "unknown"
                },
                "ReadsPerSampleHandler": {
                    "warning_threshold": "unknown",
                    "error_threshold": 243.75
                }
            }
        }
    }

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

    reports = json.loads(result.output)

    assert reports == expected_data


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

    reports = json.loads(result.output)

    assert reports == expected_data
