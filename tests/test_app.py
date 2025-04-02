from pathlib import Path

import pytest

from checkQC.app import App
from checkQC.app import run_new_checkqc


@pytest.fixture
def bcl2fastq_runfolder_path():
    return str(Path(__file__).parent / "resources/170726_D00118_0303_BCB1TVANXX/")


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

    assert exit_status == 1
    assert reports == {
        'lane reports': {
            1: {
                'error_rate': [
                    'Fatal QC error: Error rate is nan on lane 1 for read 1. '
                    'This may be because no PhiX was loaded on this lane. Use '
                    '"allow_missing_error_rate: true" to disable this error message.'
                ],
                'reads_per_sample': [
                    'Fatal QC error: Number of reads for sample '
                    'Sample_14574-Qiagen-IndexSet1-SP-Lane1 '
                    'on lane 1 were too low: 0.00992 M (threshold: 121.875 M)',
                    'Fatal QC error: Number of reads for sample '
                    'Sample_14575-Qiagen-IndexSet1-SP-Lane1 '
                    'on lane 1 were too low: 0.00856 M (threshold: 121.875 M)'
                ],
                'undetermined_percentage': [
                    'Fatal QC error: Percentage of undetermined indices '
                    '99.46% (- 0.00% phiX) > 9.00% on lane 1.'
                ],
            },
            2: {
                'error_rate': [
                    'Fatal QC error: Error rate is nan on lane 2 for read 1. '
                    'This may be because no PhiX was loaded on this lane. Use '
                    '"allow_missing_error_rate: true" to disable this error message.'
                ],
                'reads_per_sample': [
                    'Fatal QC error: Number of reads for sample '
                    'Sample_14574-Qiagen-IndexSet1-SP-Lane2 '
                    'on lane 2 were too low: 0.010208 M (threshold: 121.875 M)',
                    'Fatal QC error: Number of reads for sample '
                    'Sample_14575-Qiagen-IndexSet1-SP-Lane2 '
                    'on lane 2 were too low: 0.008672 M (threshold: 121.875 M)'
                ],
                'undetermined_percentage': [
                    'Fatal QC error: Percentage of undetermined indices '
                    '99.45% (- 0.00% phiX) > 9.00% on lane 2.'
                ]
            }
        },
        'run_summary': {
            'checkers': {
                'ClusterPFHandler': {
                    'error_threshold': 'unknown', 'warning_threshold': 325
                },
                'ErrorRateHandler': {
                    'allow_missing_error_rate': False,
                    'error_threshold': 'unknown', 'warning_threshold': 1
                },
                'Q30Handler': {
                    'error_threshold': 'unknown', 'warning_threshold': 90
                },
                'ReadsPerSampleHandler': {
                    'error_threshold': 243.75, 'warning_threshold': 'unknown'
                },
                'UndeterminedPercentageHandler': {
                    'error_threshold': 9, 'warning_threshold': 'unknown'
                },
                'UnidentifiedIndexHandler': {
                    'significance_threshold': 1,
                    'white_listed_indexes': [
                        '.*N.*', 'G{6,}'
                    ]
                }
            },
            'instrument_and_reagent_version': 'novaseq_SP',
            'read_length': 36
        },
    }
