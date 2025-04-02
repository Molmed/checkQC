import csv
import pathlib

import interop
from samshee.sectionedsheet import read_sectionedsheet

from checkQC.run_type_recognizer import RunTypeRecognizer


@classmethod
def from_bclconvert(cls, runfolder_path, parser_config):
    runfolder_path = pathlib.Path(runfolder_path)
    assert runfolder_path.is_dir()

    summary, index_summary = _read_interop_summary(runfolder_path)
    quality_metrics = _read_quality_metrics(
        runfolder_path
        / parser_config["reports_location"]
        / "Quality_Metrics.csv"
    )
    top_unknown_barcodes = _read_top_unknown_barcodes(
        runfolder_path
        / parser_config["reports_location"]
        / "Top_Unknown_Barcodes.csv"
    )
    samplesheet = _read_samplesheet(runfolder_path)

    instrument, read_length = _read_run_metadata(runfolder_path)

    sequencing_metrics = {
        lane + 1: {
            "total_cluster_pf": summary.at(0).at(lane).reads_pf(),
            "yield": sum(
                int(row["Yield"])
                for row in quality_metrics
                if row["Lane"] == str(lane + 1)
            ),
            "yield_undetermined": next(
                int(row["Yield"])
                for row in quality_metrics
                if (
                    row["Lane"] == str(lane + 1)
                    and row["SampleID"] == "Undetermined"
                )
            ),
            "top_unknown_barcodes": [
                {
                    "index": row["index"],
                    "index2": row["index2"],
                    "count": int(row["# Reads"]),
                }
                for row in top_unknown_barcodes
                if row["Lane"] == str(lane + 1)
            ],
            "reads": {
                i_read + 1: {
                    "mean_error_rate": (
                        lane_summary := summary.at(i_read).at(lane)
                    ).error_rate().mean(),
                    "percent_q30": lane_summary.percent_gt_q30(),
                    "is_index": summary.at(i_read).read().is_index(),
                    "mean_percent_phix_aligned": lane_summary.percent_aligned().mean()
                }
                for i_read in range(summary.size())
            },
            "reads_per_sample": [
                {
                    "sample_id": (
                        sample_summary := index_summary.at(lane).at(sample_no)
                    ).sample_id(),
                    "cluster_count": sample_summary.cluster_count(),
                }
                for sample_no in range(index_summary.at(lane).size())
            ],
        }
        for lane in range(summary.lane_count())
    }

    return cls(
        instrument,
        read_length,
        samplesheet,
        sequencing_metrics,
    )


def _read_interop_summary(runfolder_path):
    """
    Read interop files and return interop objects for run_summary and index
    summary.
    """

    runfolder_path = str(runfolder_path)  # interop does not handle Path objects

    run_info = interop.py_interop_run.info()
    run_info.read(runfolder_path)

    run_metrics = interop.py_interop_run_metrics.run_metrics()
    run_metrics.read(runfolder_path)

    run_summary = interop.py_interop_summary.run_summary()
    interop.py_interop_summary.summarize_run_metrics(run_metrics, run_summary)

    index_summary = interop.py_interop_summary.index_flowcell_summary()
    interop.py_interop_summary.summarize_index_metrics(run_metrics, index_summary)

    return run_summary, index_summary


def _read_quality_metrics(quality_metrics_path):
    """
    Read quality metrics file
    """
    with open(quality_metrics_path, encoding="utf-8") as csvfile:
        return list(csv.DictReader(csvfile))


def _read_top_unknown_barcodes(top_unknown_barcodes_path):
    """
    Read top unknown barcodes file
    """
    with open(top_unknown_barcodes_path, encoding="utf-8") as csvfile:
        return list(csv.DictReader(csvfile))


def _read_run_metadata(runfolder_path):
    """
    Read intrument, reagent and read_length
    """
    run_type_recognizer = RunTypeRecognizer(runfolder_path)

    return (
        run_type_recognizer.instrument_and_reagent_version(),
        # NOTE: read length can be either "151" or "151-151" in case of paired
        # reads. For now, only symetric read length is supported
        # see checkQC/app.py#L159
        int(run_type_recognizer.read_length().split("-")[0]),
    )


def _read_samplesheet(runfolder_path):
    """
    Parse `BCLConvert_Data` section of samplesheet

    NOTE: column name can sometimes start with an uppercase letter.
    """
    samplesheet = read_sectionedsheet(
        runfolder_path / "SampleSheet.csv")["BCLConvert_Data"]

    for i, row in enumerate(samplesheet):
        samplesheet[i] = {
            key.lower(): value
            for key, value in row.items()
        }

    for row in samplesheet:
        row["index"] = row["index"].replace(" ", "")
        row["index2"] = row["index2"].replace(" ", "")

    return samplesheet
