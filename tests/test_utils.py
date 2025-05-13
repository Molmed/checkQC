import json
import numpy as np
from pathlib import Path


def float_eq(a, b):
    return np.isclose(a, b) or (np.isnan(a) and np.isnan(b))


def get_stats_json(runfolder="bcl2fastq/150418_SN7001335_0149_AH32CYBCXX"):
    with open(
        Path(__file__).parent
        / "resources"
        / runfolder
        / "Stats.json"
    ) as f:
        return json.load(f)
