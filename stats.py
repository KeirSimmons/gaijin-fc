from collections import defaultdict
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from games import Games
from login import Login
from metrics import (
    Assists,
    ConcededMetric,
    DisciplinaryMetric,
    GamesMetric,
    Goals,
    HatrickMetric,
    MOTMMetric,
)
from players import Players
from promotions import Promotions
from repo import Repo


class Stats:

    METRICS = [
        GamesMetric,
        Goals,
        Assists,
        MOTMMetric,
        ConcededMetric,
        DisciplinaryMetric,
        HatrickMetric,
    ]

    def __init__(self):
        self.login = Login()
        self.login.authentication()

        self.players = Players()
        self.games = Games()

    def process(
        self,
        include_initial=True,
        include_new=True,
        games_to_include=None,
        matches_to_include=None,
        players=None,
        normalise=False,
        display=True,
        subgraph=False,
        key=None,
    ):
        self.include_initial = include_initial
        self.include_new = include_new
        self.games_to_include = games_to_include
        self.matches_to_include = matches_to_include
        self.players_to_include = players or self.players.get_data().keys()
        self.normalise = normalise
        self.subgraph = subgraph
        self.calculate_stats()
        if display:
            self.display(key=key)

    def calculate_stats(self):
        """We have two scores we want to track:

        1) The value for each metric (i.e. 5 goals)
        2) The actual calculated score each metric (i.e. 10 points if a goal counts as 2)

        We store 1) in "metrics" and 2) in "actuals"
        """

        metrics_to_consider = Stats.METRICS
        players = defaultdict(lambda: defaultdict(int))
        metrics = defaultdict(lambda: defaultdict(int))
        actuals = defaultdict(lambda: defaultdict(int))

        if self.include_new:
            for game in self.games.get():
                # If we don't want to include this game, go to the next one!
                if (
                    self.games_to_include is not None
                    and game["key"] not in self.games_to_include
                ):
                    continue
                game_data = game["game"]

                for match_id, match in enumerate(game_data["matches"]):
                    if (
                        self.matches_to_include is not None
                        and match_id not in self.matches_to_include
                    ):
                        continue
                    level = match["level"]
                    for player, player_data in match["players"].items():
                        if player not in self.players_to_include:
                            continue
                        for metric in metrics_to_consider:
                            if metric.KEY in player_data:
                                metric_val = player_data[metric.KEY]
                                # We don't count points from a game with one player
                                if len(game_data["players"]) == 1:
                                    score = 0
                                else:
                                    score = metric(metric_val).calc(level)
                                players[player][metric.KEY] += score
                                actuals[metric.KEY][player] += score
                                metrics[metric.KEY][player] += metric_val

        # Games played is different (and we only add it if including initial metrics)
        ## Why? If we are not, we're likely on a sub-graph
        for player in self.players_to_include:
            player_data = self.players.get_data(player)
            games_played = 0
            player_game_data = self.games.get()
            if self.include_new and player_game_data:
                games_played = sum(
                    [
                        1
                        for game in player_game_data
                        if player in game["game"]["players"]
                    ]
                )
            if self.include_initial:
                games_played += player_data["initial_metrics"].get("games") or 0
            players[player][GamesMetric.KEY] = games_played
            actuals[GamesMetric.KEY][player] = 0  # no points for games played
            metrics[GamesMetric.KEY][player] = games_played

        # Now add initial data
        if self.include_initial:
            for player in self.players_to_include:
                player_data = self.players.get_data(player)
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

    def display(self, key=None):

        additional_metrics = ["Points"]

        data = self.stats["metrics"]
        players = self.players_to_include

        data["Points"] = {
            player: sum(
                (val.get(player) or 0) for _, val in self.stats["actuals"].items()
            )
            for player in players
        }

        additional_metrics.append("PPG")
        data["PPG"] = {
            player: (
                0
                if (
                    data["Points"].get(player) is None
                    or data["Points"].get(player) == 0
                )
                else data["Points"].get(player)
                / max(1, (self.stats["metrics"][GamesMetric.KEY].get(player) or 0))
            )
            for player in players
        }

        # Display a progress bar for the next promotion
        self.points = sum([val for val in data["Points"].values()])

        if self.normalise and GamesMetric.KEY in data:
            for metric, player_vals in data.items():
                if metric in ["PPG", GamesMetric.KEY]:
                    continue
                for player in players:
                    player_vals[player] = player_vals[player] / max(
                        1, data[GamesMetric.KEY][player]
                    )
            for metric, player_vals in data.items():
                max_val = max([val for val in player_vals.values()])
                if metric in ["PPG", GamesMetric.KEY]:
                    continue
                for player in players:
                    player_vals[player] = player_vals[player] / max(1, max_val)
            del data["PPG"]
            del data[GamesMetric.KEY]

        if self.subgraph:
            if "PPG" in data:
                del data["PPG"]
            if GamesMetric.KEY in data:
                del data[GamesMetric.KEY]

        metric_order = [*additional_metrics, *Stats.METRICS]
        valid_metrics = [
            metric
            for metric, player_vals in data.items()
            if sum(player_vals.values()) != 0
        ]

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
                            if (metric if isinstance(metric, str) else metric.KEY)
                            in valid_metrics
                        ]
                    ],
                )
                for metric in metric_order
            ]
        )
        if key is not None:
            st.plotly_chart(fig, key=key)
        else:
            st.plotly_chart(fig)
        self.data = data

    def get_points(self):
        return self.points

    def process_historical(self, player):
        x = []
        y = defaultdict(list)
        largest = defaultdict(lambda: -np.inf)
        metrics = [Goals, Assists, HatrickMetric, ConcededMetric, DisciplinaryMetric]

        for game in sorted(
            self.games.get(),
            key=lambda x: datetime.strptime(x["game"]["date"], "%Y-%m-%d"),
        ):
            match_data = game["game"]["matches"]
            if player not in game["game"]["players"]:
                continue
            extracted_metrics = {
                metric.KEY: sum(
                    (match["players"][player].get(metric.KEY) or 0)
                    for match in match_data
                )
                for metric in metrics
            }
            x.append(game["game"]["date"])
            st.write()
            for metric in metrics:
                val = extracted_metrics.get(metric.KEY) or 0
                y[metric.KEY].append(val)
                largest[metric.KEY] = max(largest[metric.KEY], val)

        fig = go.Figure()
        for metric in metrics:
            fig.add_trace(
                go.Scatter(
                    x=x,
                    y=(
                        np.zeros_like(y[metric.KEY])
                        if largest[metric.KEY] == 0
                        else np.asarray(y[metric.KEY]) / largest[metric.KEY]
                    ),
                    mode="markers+lines",
                    name=metric.GRAPH_LABEL,
                )
            )
        fig.update_traces(marker_size=10)
        fig.update_layout(title="Progress")

        st.plotly_chart(fig)


if __name__ == "__main__":
    Stats().process()
