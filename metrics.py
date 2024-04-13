import streamlit as st


class Metric:

    INITIAL_METRICS_KEY = "initial_metrics"
    ENJOY_MULTIPLIER = 1
    GACHI_MULTIPLIER = 1

    def __init__(self, val=None):
        self.val = val
        self.val = self.format()

    def format(self):
        return self.val

    def valid(self):
        raise NotImplementedError

    def ask(self):
        raise NotImplementedError

    def get(self):
        return self.val

    def calc(self, level):
        if level == "Enjoy":
            return self.calc_enjoy()
        elif level == "Gachi":
            return self.calc_gachi()
        raise Exception(f"Invalid game level found ({level})")

    def calc_enjoy(self):
        return self.val * self.ENJOY_MULTIPLIER

    def calc_gachi(self):
        return self.val * self.GACHI_MULTIPLIER


class GamesMetric(Metric):
    KEY = "games"
    MATCH_LABEL = "Games played?"
    GRAPH_LABEL = "Games"

    def __init__(self, val=None):
        super().__init__(val)

    def format(self):
        return int(self.val) if self.val is not None else None

    def valid(self):
        return self.val >= 0

    def ask(self):
        return st.number_input(self.MATCH_LABEL, min_value=0, step=1, value=self.val)


class Goals(Metric):
    KEY = "goals"
    MATCH_LABEL = "Goals scored?"
    GRAPH_LABEL = "Goals"

    def __init__(self, val=None):
        super().__init__(val)

    def format(self):
        return int(self.val) if self.val is not None else None

    def valid(self):
        return self.val >= 0

    def ask(self):
        return st.number_input(self.MATCH_LABEL, min_value=0, step=1, value=self.val)


class Assists(Metric):
    KEY = "assists"
    MATCH_LABEL = "Assists?"
    GRAPH_LABEL = "Assists"

    ENJOY_MULTIPLIER = 0.5
    GACHI_MULTIPLIER = 0.5

    def __init__(self, val=None):
        super().__init__(val)

    def format(self):
        return int(self.val) if self.val is not None else None

    def valid(self):
        return self.val >= 0

    def ask(self):
        return st.number_input(self.MATCH_LABEL, min_value=0, step=1, value=self.val)


class MOTMMetric(Metric):
    KEY = "MOTM"
    MATCH_LABEL = "MOTM?"
    GRAPH_LABEL = "MOTM"

    ENJOY_MULTIPLIER = 0.5
    GACHI_MULTIPLIER = 0.5

    def __init__(self, val=None):
        super().__init__(val)

    def format(self):
        return int(self.val) if self.val is not None else None

    def valid(self):
        return self.val >= 0

    def ask(self):
        return st.number_input(self.MATCH_LABEL, min_value=0, step=1, value=self.val)


class ConcededMetric(Metric):
    KEY = "conceded"
    MATCH_LABEL = "Conceded?"
    GRAPH_LABEL = "Conceded"

    ENJOY_MULTIPLIER = -1
    GACHI_MULTIPLIER = 0

    def __init__(self, val=None):
        super().__init__(val)

    def format(self):
        return int(self.val) if self.val is not None else None

    def valid(self):
        return self.val >= 0

    def ask(self):
        return st.number_input(self.MATCH_LABEL, min_value=0, step=1, value=self.val)


class DisciplinaryMetric(Metric):
    KEY = "disciplinary"
    MATCH_LABEL = "Disciplinaries?"
    GRAPH_LABEL = "OG / Discip."

    ENJOY_MULTIPLIER = -2
    GACHI_MULTIPLIER = -2

    def __init__(self, val=None):
        super().__init__(val)

    def format(self):
        return int(self.val) if self.val is not None else None

    def valid(self):
        return self.val >= 0

    def ask(self):
        return st.number_input(self.MATCH_LABEL, min_value=0, step=1, value=self.val)
