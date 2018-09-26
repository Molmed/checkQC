
import json
import os


def get_stats_json(runfolder="150418_SN7001335_0149_AH32CYBCXX"):
    with open(os.path.join(
            os.path.dirname(__file__),
            "resources",
            runfolder,
            "Stats.json")) as f:
        return json.load(f)
