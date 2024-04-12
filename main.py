from collections import defaultdict

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from games import Games
from metrics import Assists, GamesMetric, Goals
from players import Players
from repo import Repo


class Main:

    METRICS = [GamesMetric, Goals, Assists]

    def __init__(self):
        st.set_page_config(page_title="Main")
        self.players = Players()
        self.games = Games()
        self.calculate_stats()
        self.display()

    def calculate_stats(self):
        metrics_to_consider = Main.METRICS
        players = defaultdict(lambda: defaultdict(int))
        metrics = defaultdict(lambda: defaultdict(int))
        for game in self.games.get():
            game_data = game["game"]
            for match in game_data["matches"]:
                level = match["level"]
                for player, player_data in match["players"].items():
                    for metric in metrics_to_consider:
                        if metric.KEY in player_data:
                            score = metric(player_data[metric.KEY]).calc(level)
                            players[player][metric.KEY] += score
                            metrics[metric.KEY][player] += score

        # Games played is different
        for player, player_data in self.players.get_data().items():
            if self.games.get():
                games_played = sum(
                    [1 if player in self.games.get()[0]["game"]["players"] else 0]
                )
            else:
                games_played = 0

            players[player][GamesMetric.KEY] = games_played
            metrics[GamesMetric.KEY][player] = games_played

        # TODO: Display the actual count, total should use multiplier

        # Now add initial data
        for player, player_data in self.players.get_data().items():
            for metric in metrics_to_consider:
                if metric.KEY in player_data["initial_metrics"]:
                    # Assume enjoy level for all of these
                    initial_score = metric(
                        player_data["initial_metrics"][metric.KEY]
                    ).calc("Enjoy")
                    players[player][metric.KEY] += initial_score
                    metrics[metric.KEY][player] += initial_score

        self.stats = {"player": players, "metric": metrics}

    def display(self):

        data = self.stats["metric"]
        players = self.players.get_data().keys()

        data["Points"] = {
            player: sum((val.get(player) or 0) for _, val in data.items())
            for player in players
        }

        metric_order = ["Points", *Main.METRICS]

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

        if st.button("Save changes?"):
            Repo()


if __name__ == "__main__":
    Main()
