from collections import namedtuple
import pytest
import numpy as np

from checkQC.qc_checkers import undetermined_percentage
from checkQC.handlers.qc_handler import QCErrorFatal, QCErrorWarning

from tests.test_utils import float_eq


def test_error_threshold():
    qc_data =  namedtuple("QCData", "sequencing_metrics")(
        {
            1: {
                "yield": 10,
                "yield_undetermined": 2,
                "reads": {
                    1: {"mean_percent_phix_aligned": 1.},
                    2: {"mean_percent_phix_aligned": 1.},
                },
            },
        }
    )

    qc_reports = undetermined_percentage(
        qc_data,
        error_threshold=15.,
        warning_threshold=5.,
    )

    assert len(qc_reports) == 1
    assert qc_reports[0].type() == "error"
    assert str(qc_reports[0]) == "Fatal QC error: Percentage of undetermined indices 19.00% > 15.00% on lane 1."
    assert qc_reports[0].data == {
        "lane": 1,
        "percentage_undetermined": 19.,
        "threshold": 15.,
    }


def test_warning_threshold():
    qc_data =  namedtuple("QCData", "sequencing_metrics")(
        {
            1: {
                "yield": 10,
                "yield_undetermined": 2,
                "reads": {
                    1: {"mean_percent_phix_aligned": 1.},
                    2: {"mean_percent_phix_aligned": 1.},
                },
            },
        }
    )

    qc_reports = undetermined_percentage(
        qc_data,
        error_threshold="unknown",
        warning_threshold=5.,
    )

    assert len(qc_reports) == 1
    assert qc_reports[0].type() == "warning"
    assert str(qc_reports[0]) == "QC warning: Percentage of undetermined indices 19.00% > 5.00% on lane 1."
    assert qc_reports[0].data == {
        "lane": 1,
        "percentage_undetermined": 19.,
        "threshold": 5.,
    }


def test_unknown_thresholds():
    qc_data =  namedtuple("QCData", "sequencing_metrics")(
        {
            1: {
                "yield": 10,
                "yield_undetermined": 2,
                "reads": {
                    1: {"mean_percent_phix_aligned": 1.},
                    2: {"mean_percent_phix_aligned": 1.},
                },
            },
        }
    )

    qc_reports = undetermined_percentage(
        qc_data,
        error_threshold="unknown",
        warning_threshold="unknown",
    )

    assert not qc_reports


def test_multiple_reports():
    qc_data =  namedtuple("QCData", "sequencing_metrics")(
        {
            1: {
                "yield": 10,
                "yield_undetermined": 2,
                "reads": {
                    1: {"mean_percent_phix_aligned": 1.},
                    2: {"mean_percent_phix_aligned": 1.},
                },
            },
            2: {
                "yield": 100,
                "yield_undetermined": 10,
                "reads": {
                    1: {"mean_percent_phix_aligned": 1.},
                    2: {"mean_percent_phix_aligned": 1.},
                }
            },
            3: {
                "yield": 100,
                "yield_undetermined": 2,
                "reads": {
                    1: {"mean_percent_phix_aligned": 1.},
                    2: {"mean_percent_phix_aligned": 1.},
                }
            },
        }
    )

    qc_reports = undetermined_percentage(
        qc_data,
        error_threshold=15.,
        warning_threshold=5.,
    )

    assert len(qc_reports) == 2
    for report in qc_reports:
        match report.data["lane"]:
            case 1:
                assert report.type() == "error"
                assert str(report) == "Fatal QC error: Percentage of undetermined indices 19.00% > 15.00% on lane 1."
                assert report.data == {
                    "lane": 1,
                    "percentage_undetermined": 19.,
                    "threshold": 15.,
                }
            case 2:
                assert report.type() == "warning"
                assert str(report) == "QC warning: Percentage of undetermined indices 9.00% > 5.00% on lane 2."
                assert report.data == {
                    "lane": 2,
                    "percentage_undetermined": 9.,
                    "threshold": 5.,
                }
            case _:
                assert False, f"An error was unexpectedly reported for lane {report.data['lane']}"


def test_yield_0():
    qc_data =  namedtuple("QCData", "sequencing_metrics")(
        {
            1: {
                "yield": 0,
                "yield_undetermined": 0,
                "reads": {
                    1: {"mean_percent_phix_aligned": 0.3},
                    2: {"mean_percent_phix_aligned": 0.1},
                },
            },
        }
    )

    qc_reports = undetermined_percentage(
        qc_data,
        error_threshold=15.,
        warning_threshold=5.,
    )

    assert len(qc_reports) == 1
    assert qc_reports[0].type() == "error"
    assert str(qc_reports[0]) == "Fatal QC error: Yield for lane 1 was 0. No undetermined percentage could be computed"
    assert qc_reports[0].data == {"lane": 1, "percentage_undetermined": None}


def test_mean_percent_phix_nan():
    qc_data =  namedtuple("QCData", "sequencing_metrics")(
        {
            3: {
                "yield": 10,
                "yield_undetermined": 2,
                "reads": {
                    1: {"mean_percent_phix_aligned": np.nan},
                    2: {"mean_percent_phix_aligned": 1.},
                },
            },
        }
    )

    qc_reports = undetermined_percentage(
        qc_data,
        error_threshold=15.,
        warning_threshold=5.,
    )

    assert len(qc_reports) == 1
    assert qc_reports[0].type() == "error"
    assert str(qc_reports[0]) == "Fatal QC error: Percentage of undetermined indices 19.00% > 15.00% on lane 3."
    assert qc_reports[0].data == {
        "lane": 3,
        "percentage_undetermined": 19.,
        "threshold": 15.,
    }
