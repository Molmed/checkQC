
import json


def get_stats_json():
    with open("Stats.json") as f:
        return json.load(f)
