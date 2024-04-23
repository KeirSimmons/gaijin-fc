import random

import streamlit as st


class Metric:

    INITIAL_METRICS_KEY = "initial_metrics"
    ENJOY_MULTIPLIER = 1
    GACHI_MULTIPLIER = 1

    def __init__(self, val=None, key=None):
        self.val = val
        self.val = self.format()
        self._key = str(random.random()) if key is None else key

    def format(self):
        return self.val

    def valid(self):
        raise NotImplementedError

    def initial_ask(self):
        # The specific form to use on the initial page (if different to a game)
        return self.ask()

    def ask(self):
        raise NotImplementedError

    def get(self):
        return self.val

    def calc(self, level):
        if level == "Enjoy":
            multiplier = self.ENJOY_MULTIPLIER
        elif level == "Gachi":
            multiplier = self.GACHI_MULTIPLIER
        else:
            raise Exception(f"Invalid game level found ({level})")
        return self.val * multiplier


class GamesMetric(Metric):
    KEY = "games"
    MATCH_LABEL = "Games played?"
    GRAPH_LABEL = "Games"

    # No points for playing!
    ENJOY_MULTIPLIER = 0
    GACHI_MULTIPLIER = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def format(self):
        return int(self.val) if self.val is not None else None

    def valid(self):
        return self.val >= 0

    def ask(self):
        return st.number_input(
            self.MATCH_LABEL, min_value=0, step=1, key=self._key, value=self.val
        )


class Goals(Metric):
    KEY = "goals"
    MATCH_LABEL = "Goals scored?"
    GRAPH_LABEL = "Goals"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def format(self):
        return int(self.val) if self.val is not None else None

    def valid(self):
        return self.val >= 0

    def ask(self):
        return st.number_input(
            self.MATCH_LABEL, min_value=0, step=1, key=self._key, value=self.val
        )


class Assists(Metric):
    KEY = "assists"
    MATCH_LABEL = "Assists?"
    GRAPH_LABEL = "Assists"

    ENJOY_MULTIPLIER = 0.5
    GACHI_MULTIPLIER = 0.5

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def format(self):
        return int(self.val) if self.val is not None else None

    def valid(self):
        return self.val >= 0

    def ask(self):
        return st.number_input(
            self.MATCH_LABEL, min_value=0, step=1, key=self._key, value=self.val
        )


class MOTMMetric(Metric):
    KEY = "MOTM"
    MATCH_LABEL = "MOTM?"
    GRAPH_LABEL = "MOTM"

    ENJOY_MULTIPLIER = 0.5
    GACHI_MULTIPLIER = 0.5

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def format(self):
        return int(self.val) if self.val is not None else None

    def valid(self):
        return self.val >= 0

    def initial_ask(self):
        return st.number_input(
            self.MATCH_LABEL, min_value=0, step=1, key=self._key, value=self.val
        )

    def ask(self):
        return st.toggle(self.MATCH_LABEL, key=self._key)


class ConcededMetric(Metric):
    KEY = "conceded"
    MATCH_LABEL = "Conceded?"
    GRAPH_LABEL = "Conceded"

    ENJOY_MULTIPLIER = -1
    GACHI_MULTIPLIER = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def format(self):
        return int(self.val) if self.val is not None else None

    def valid(self):
        return self.val >= 0

    def ask(self):
        return st.number_input(
            self.MATCH_LABEL, min_value=0, step=1, key=self._key, value=self.val
        )


class DisciplinaryMetric(Metric):
    KEY = "disciplinary"
    MATCH_LABEL = "Disciplinaries?"
    GRAPH_LABEL = "OG / Discip."

    ENJOY_MULTIPLIER = -2
    GACHI_MULTIPLIER = -2

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def format(self):
        return int(self.val) if self.val is not None else None

    def valid(self):
        return self.val >= 0

    def ask(self):
        return st.number_input(
            self.MATCH_LABEL, min_value=0, step=1, key=self._key, value=self.val
        )


class HatrickMetric(Metric):
    KEY = "hatrick"
    MATCH_LABEL = "Hat tricks?"
    GRAPH_LABEL = "Hat tricks"

    ENJOY_MULTIPLIER = 1
    GACHI_MULTIPLIER = 2

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def format(self):
        return int(self.val) if self.val is not None else None

    def valid(self):
        return self.val >= 0

    def ask(self):
        return st.number_input(
            self.MATCH_LABEL, min_value=0, step=1, key=self._key, value=self.val
        )
