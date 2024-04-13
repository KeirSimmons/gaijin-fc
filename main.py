from collections import defaultdict

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from games import Games
from metrics import (
    Assists,
    ConcededMetric,
    DisciplinaryMetric,
    GamesMetric,
    Goals,
    MOTMMetric,
)
from players import Players
from repo import Repo


class Main:

    METRICS = [
        GamesMetric,
        Goals,
        Assists,
        MOTMMetric,
        ConcededMetric,
        DisciplinaryMetric,
    ]

    def __init__(self):
        st.set_page_config(page_title="Main")
        self.players = Players()
        self.games = Games()
        self.calculate_stats()
        self.display()

    def calculate_stats(self):
        """We have two scores we want to track:

        1) The value for each metric (i.e. 5 goals)
        2) The actual calculated score each metric (i.e. 10 points if a goal counts as 2)

        We store 1) in "metrics" and 2) in "actuals"
        """

        metrics_to_consider = Main.METRICS
        players = defaultdict(lambda: defaultdict(int))
        metrics = defaultdict(lambda: defaultdict(int))
        actuals = defaultdict(lambda: defaultdict(int))

        for game in self.games.get():
            game_data = game["game"]
            for match in game_data["matches"]:
                level = match["level"]
                for player, player_data in match["players"].items():
                    for metric in metrics_to_consider:
                        if metric.KEY in player_data:
                            metric_val = player_data[metric.KEY]
                            score = metric(metric_val).calc(level)
                            players[player][metric.KEY] += score
                            actuals[metric.KEY][player] += score
                            metrics[metric.KEY][player] += metric_val

        # Games played is different
        for player, player_data in self.players.get_data().items():
            if self.games.get():
                games_played = sum(
                    [1 if player in self.games.get()[0]["game"]["players"] else 0]
                )
            else:
                games_played = 0
            players[player][GamesMetric.KEY] = games_played
            actuals[GamesMetric.KEY][player] = games_played
            metrics[GamesMetric.KEY][player] = games_played

        # Now add initial data
        for player, player_data in self.players.get_data().items():
            for metric in metrics_to_consider:
                if metric.KEY in player_data["initial_metrics"]:
                    # Assume enjoy level for all of these
                    metric_val = player_data["initial_metrics"][metric.KEY]
                    initial_score = metric(metric_val).calc("Enjoy")
                    players[player][metric.KEY] += initial_score
                    actuals[metric.KEY][player] += initial_score
                    metrics[metric.KEY][player] += metric_val

        self.stats = {
            "player": players,
            "actuals": actuals,
            "metrics": metrics,
        }

    def display(self):

        data = self.stats["metrics"]
        players = self.players.get_data().keys()

        data["Points"] = {
            player: sum(
                (val.get(player) or 0) for _, val in self.stats["actuals"].items()
            )
            for player in players
        }

        data["PPG"] = {
            player: (
                0
                if (
                    data["Points"].get(player) is None
                    or data["Points"].get(player) == 0
                )
                else (self.stats["actuals"][GamesMetric.KEY].get(player) or 0)
                / data["Points"].get(player)
            )
            for player in players
        }

        metric_order = ["Points", "PPG", *Main.METRICS]

        fig = go.Figure(
            data=[
                go.Bar(
                    name=metric if isinstance(metric, str) else metric.GRAPH_LABEL,
                    x=list(players),
                    y=[
                        *[
                            data[metric if isinstance(metric, str) else metric.KEY][
                                player
                            ]
                            for player in players
                        ]
                    ],
                )
                for metric in metric_order
            ]
        )
        st.plotly_chart(fig)

        self.promotions(sum([val for val in data["Points"].values()]))

        if st.button("Save changes?"):
            Repo()

    def promotions(self, points):
        promos = [["celtic", 0], ["rangers", 100], ["brighton", 250]]
        if len(promos) < 2 or promos[0][1] > 0:
            st.exception("Promotion data not sufficient.")
        current_level = None
        next_level = None
        for team, point_requirement in promos:
            if points >= point_requirement:
                current_level = [team, point_requirement]
            else:
                next_level = [team, point_requirement]
                break

        zero_level = current_level[1]
        max_level = next_level[1]

        progress = (points - zero_level) / (max_level - zero_level)

        st.progress(
            progress,
            text=f"{points} / {point_requirement} points - next promotion: {next_level[0]}",
        )


if __name__ == "__main__":
    Main()
