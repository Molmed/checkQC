import json


def basic_view(checker_configs, qc_data, qc_reports):
    """
    Return qc reports as well as basic info about the sequencing data.
    """
    data = {
        "reports": [str(report) for report in qc_reports],
        "run_summary": {
            "instrument_and_reagent_version": qc_data.instrument,
            "read_length": qc_data.read_length,
            "checkers": checker_configs,
        }
    }

    return json.dumps(data, indent=True)
