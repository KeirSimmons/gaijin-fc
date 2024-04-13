import json

import streamlit as st

from metrics import (
    Assists,
    ConcededMetric,
    DisciplinaryMetric,
    GamesMetric,
    Goals,
    Metric,
    MOTMMetric,
)


class Players:

    METRICS = {
        metric_class.KEY: metric_class
        for metric_class in [
            GamesMetric,
            Goals,
            Assists,
            MOTMMetric,
            ConcededMetric,
            DisciplinaryMetric,
        ]
    }

    FILE = "./players.json"

    def __init__(self):
        self.load()

    def load(self):
        self._has_changes = False
        with open(Players.FILE) as file:
            self.data = json.load(file)

    def save(self):
        with open(Players.FILE, "w") as file:
            json.dump(self.data, file, indent=4, sort_keys=True)

    def get(self, player, attr):
        return self.data[player].get(attr)

    def get_initial_metric(self, player, metric):
        return self.get(player, "initial_metrics").get(metric)

    def get_data(self):
        return self.data

    def set_initial_metrics(self, player_id, params=None):
        # First convert params to a dict if necessary
        if params is None:
            params = {}

        for key, value in params.items():
            self.set(player_id, key, value, initial_metric=True)

        self.save()

    def set(self, player_id, key, value, initial_metric=False):
        if key not in Players.METRICS:
            # Invalid key
            raise KeyError(f"Invalid metric passed ({key})")
        elif value is None:
            # Remove this key
            if initial_metric:
                if key in self.data[player_id][Metric.INITIAL_METRICS_KEY]:
                    del self.data[player_id][key]
            else:
                if key in self.data[player_id]:
                    del self.data[player_id][key]
        else:
            # Set the key to this value
            param = Players.METRICS[key](value)
            updated_val = param.get()  # Post-formatting, validation
            if initial_metric:
                if (
                    key not in self.data[player_id][Metric.INITIAL_METRICS_KEY]
                    or self.data[player_id][Metric.INITIAL_METRICS_KEY][key]
                    != updated_val
                ):
                    self.data[player_id][Metric.INITIAL_METRICS_KEY][key] = updated_val
            else:
                if (
                    key not in self.data[player_id]
                    or self.data[player_id][key] != updated_val
                ):
                    self.data[player_id][key] = updated_val
