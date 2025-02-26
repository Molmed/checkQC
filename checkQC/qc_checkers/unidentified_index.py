import re
import functools

from checkQC.qc_checkers.utils import get_complement
from checkQC.handlers.qc_handler import QCErrorWarning

def unidentified_index(
    qc_data,
    significance_threshold,
    white_listed_indexes=None,
):
    """
    Identify unidentified indices with are significantly overrepresented
    and suggest possible causes based on the indices found in the samplesheet.
    """
    if white_listed_indexes is None:
        white_listed_indexes = []
    significance_threshold /= 100.

    for i, re_index in enumerate(white_listed_indexes):
        white_listed_indexes[i] = re.compile(re_index)

    samplesheet_matcher = SamplesheetMatcher(qc_data.samplesheet)

    qc_warnings = []

    for lane, lane_data in qc_data.sequencing_metrics.items():
        for barcode in lane_data["top_unknown_barcodes"]:
            significance = barcode["count"] / lane_data["total_cluster_pf"]
            if significance < significance_threshold:
                continue
            index = (
                f"{barcode['index']}+{barcode['index2']}"
                if barcode.get("index2") else
                barcode["index"]
            )

            data = {
                "index": index,
                "lane": lane,
                "causes": [],
            }
            msg = (
                f"Overrepresented unknown barcode: {data['index']} "
                f"({significance*100.:.1f}% > {significance_threshold*100.:.1f}%)."
            )
            if any(
                re_allowed_index.match(index)
                for re_allowed_index in white_listed_indexes
            ):
                msg += " This barcode is white-listed."
            else:
                causes = samplesheet_matcher.list_causes(barcode)
                if causes:
                    msg += '\nPossible causes are:\n' + '\n'.join(
                        [f"- {m}" for m, _ in causes]
                    )
                for _, cause_data in causes:
                    data["causes"].append(cause_data)

            qc_warnings.append(QCErrorWarning(msg=msg, data=data))

    return qc_warnings


class SamplesheetMatcher:
    """
    A class to identify potential index mismatches.
    """
    def __init__(self, samplesheet):
        """
        Build SamplesheetMatcher from samplesheet object

        Builds an index of all the indices in the samplesheet in order to
        quickly look them up.
        """
        self.samplesheet_single_indices = {}
        self.samplesheet_dual_indices = {}
        for row in samplesheet:
            if row.get("Index2"):
                self.samplesheet_dual_indices.setdefault(
                    row["Index"], []).append(row)
                self.samplesheet_dual_indices.setdefault(
                    row["Index2"], []).append(row)
                self.samplesheet_dual_indices.setdefault(
                    f"{row['Index']}+{row['Index2']}", []).append(row)
            else:
                self.samplesheet_single_indices.setdefault(
                    row["Index"], []).append(row)

    def list_causes(self, barcode):
        """
        returns a list of causes (msg + data)
        """
        causes = []
        causes.extend(self.check_complement_and_reverse(barcode))
        causes.extend(self.check_lane_swap(barcode))
        if barcode.get("index2"):
            causes.extend(self.check_dual_index_swap(barcode))

        return causes

    def check_complement_and_reverse(self, barcode):
        """
        Check if reverse, complement and reverse complement indices exist in
        the samplesheet.
        """
        causes = []

        indices = [barcode["index"]]
        if barcode.get("index2"):
            indices.append(barcode["index2"])

        samplesheet_indices = (
            self.samplesheet_dual_indices
            if barcode.get("index2")
            else self.samplesheet_single_indices
        )

        for index in indices:
            for cause, variation in [
                ("reverse", index[::-1]),
                ("complement", get_complement(index)),
                ("reverse complement", get_complement(index)[::-1]),
            ]:
                for row in samplesheet_indices.get(variation, []):
                    msg = (
                        f"{cause} index \"{variation}\" found in samplesheet"
                        f" for sample {row['Sample_ID']}, lane {row['Lane']}"
                    )
                    data = (cause, row)
                    causes.append((msg, data))

        return causes

    def check_lane_swap(self, barcode):
        """
        Check if barcode is found on a different lane in the samplesheet.
        """
        index = (
            f"{barcode['index']}+{barcode['index2']}"
            if barcode.get("index2") else
            barcode["index"]
        )

        samplesheet_indices = (
            self.samplesheet_dual_indices
            if barcode.get("index2")
            else self.samplesheet_single_indices
        )

        causes = []
        for row in samplesheet_indices.get(index, []):
            if row["Lane"] != barcode["lane"]:
                msg = f"index {index} found on lane {row['Lane']}"
                data = ("lane swap", row)
                causes.append((msg, data))

        return causes


    def check_dual_index_swap(self, barcode):
        """
        Check if dual indices have been swapped in samplesheet.
        """
        causes = []
        swaped_index = f"{barcode['index2']}+{barcode['index']}"
        for row in self.samplesheet_dual_indices.get(swaped_index, []):
            msg = (
                f"dual index swap: barcode \"{swaped_index}\" found"
                f" in samplesheet for sample {row['Sample_ID']}, lane {row['Lane']}",
            )
            data = ("dual index swap", row)
            causes.append((msg, data))

        return causes
