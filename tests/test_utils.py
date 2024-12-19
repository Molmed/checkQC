import json
import numpy as np
import os


def float_eq(a, b):
    return np.isclose(a, b) or (np.isnan(a) and np.isnan(b))


def get_stats_json(runfolder="150418_SN7001335_0149_AH32CYBCXX"):
    with open(os.path.join(
            os.path.dirname(__file__),
            "resources",
            runfolder,
            "Stats.json")) as f:
        return json.load(f)
