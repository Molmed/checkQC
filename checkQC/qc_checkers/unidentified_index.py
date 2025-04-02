import re
import functools

from checkQC.qc_checkers.utils import get_complement
from checkQC.handlers.qc_handler import QCErrorWarning, QCErrorFatal

def unidentified_index(
    qc_data,
    significance_threshold,
    white_listed_indexes=None,
):
    """
    Identify unidentified indices with are significantly overrepresented
    and suggest possible causes based on the indices found in the samplesheet.

    Possible causes are:
    - swap between the first and second index
    - the index is present on another lane
    - the index complement, reverse or reverse complement is found in the
    samplesheet.

    Parameters:
    -----------
    qc_data: QCData
        sequencing data to investigate
    significance_threshold: float
        threshold above which errors should be reported (in % on the total read
        counts for that lane)
    white_listed_indexes: [str]
        list of regexes. Indices matching this regex will be reported as
        warnings instead of errors.
    """
    samplesheet_matcher = SamplesheetMatcher(qc_data.samplesheet)

    white_listed_indexes = [
        re.compile(re_index)
        for re_index in white_listed_indexes
    ] if white_listed_indexes else []

    qc_errors = []
    for lane, lane_data in qc_data.sequencing_metrics.items():
        for barcode in lane_data["top_unknown_barcodes"]:
            significance = barcode["count"] / lane_data["total_cluster_pf"] * 100.
            if significance < significance_threshold:
                continue
            index = (
                f"{barcode['index']}+{barcode['index2']}"
                if barcode.get("index2") else
                barcode["index"]
            )
            is_white_listed = any(
                re_allowed_index.match(index)
                for re_allowed_index in white_listed_indexes
            )

            barcode_data = {
                "barcode": barcode.copy(),
                "is_white_listed": is_white_listed,
                "significance": significance,
                "threshold": significance_threshold,
                "lane": lane,
                "causes": [],
                "qc_checker": "unidentified_index",
            }
            msg = (
                f"Overrepresented unknown barcode \"{index}\" on lane {lane} "
                f"({significance:.1f}% > {significance_threshold:.1f}%)."
                + (" This barcode is white-listed." if is_white_listed else "")
            )

            causes = samplesheet_matcher.list_causes(barcode_data)
            if causes:
                msg += '\nPossible causes are:\n' + '\n'.join(
                    [f"- {m}" for m, _ in causes]
                )
                for _, cause_data in causes:
                    barcode_data["causes"].append(cause_data)

            qc_errors.append(
                (QCErrorWarning if is_white_listed else QCErrorFatal)(
                    msg=msg, data=barcode_data
                )
            )

    return qc_errors


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
            if row.get("index2"):
                self.samplesheet_dual_indices.setdefault(
                    row["index"], []).append(row)
                self.samplesheet_dual_indices.setdefault(
                    row["index2"], []).append(row)
                self.samplesheet_dual_indices.setdefault(
                    f"{row['index']}+{row['index2']}", []).append(row)
            else:
                self.samplesheet_single_indices.setdefault(
                    row["index"], []).append(row)

    def list_causes(self, barcode_data):
        """
        returns a list of causes (msg + data)
        """
        causes = []
        causes.extend(self.check_complement_and_reverse(barcode_data))
        causes.extend(self.check_lane_swap(barcode_data))
        if barcode_data["barcode"].get("index2"):
            causes.extend(self.check_dual_index_swap(barcode_data))

        return causes

    def check_complement_and_reverse(self, barcode_data):
        """
        Check if reverse, complement and reverse complement indices exist in
        the samplesheet.
        """
        causes = []
        barcode = barcode_data["barcode"]

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
                        f"{cause} index swap: \"{variation}\" found in samplesheet"
                        f" for sample \"{row['Sample_ID']}\", lane {row['Lane']}"
                    )
                    data = (cause, row)
                    causes.append((msg, data))

        return causes

    def check_lane_swap(self, barcode_data):
        """
        Check if barcode is found on a different lane in the samplesheet.
        """
        barcode = barcode_data["barcode"]
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
            if row["Lane"] != barcode_data["lane"]:
                msg = (
                    f"lane swap: index \"{index}\" found in samplesheet "
                    f"for sample \"{row['Sample_ID']}\", lane {row['Lane']}"
                )
                data = ("lane swap", row)
                causes.append((msg, data))

        return causes


    def check_dual_index_swap(self, barcode_data):
        """
        Check if dual indices have been swapped in samplesheet.
        """
        causes = []
        barcode = barcode_data["barcode"]
        swaped_index = f"{barcode['index2']}+{barcode['index']}"
        for row in self.samplesheet_dual_indices.get(swaped_index, []):
            msg = (
                f"dual index swap: barcode \"{swaped_index}\" found"
                f" in samplesheet for sample \"{row['Sample_ID']}\", lane {row['Lane']}"
            )
            data = ("dual index swap", row)
            causes.append((msg, data))

        return causes
