import pandas as pd
import streamlit as st

from login import Login
from metrics import Assists, ConcededMetric, GamesMetric, Goals, MOTMMetric
from players import Players


class PlayersPage:
    METRICS = {
        metric_class.KEY: metric_class
        for metric_class in [GamesMetric, Goals, Assists, MOTMMetric, ConcededMetric]
    }

    def __init__(self):
        self.login = Login()
        self.login.authentication()

        self.players = Players()

    def render(self):
        players = self.players.get_data()
        player = st.selectbox("Edit player", options=players.keys())

        if "player_edited" in st.session_state:
            st.success(
                f"Successfully edited {st.session_state['player_edited']}'s initial stats"
            )
            del st.session_state["player_edited"]

        if player:
            with st.expander("Editing **initial** stats:", expanded=True):
                with st.form(f"edit-player-{player}"):
                    form_data = {"player": player}
                    for metric in PlayersPage.METRICS.values():
                        current_val = self.players.get_initial_metric(
                            player, metric.KEY
                        )
                        form_data[metric.KEY] = {
                            "metric": metric,
                            "val": metric(current_val).ask(),
                        }

                    submit = st.form_submit_button("Edit")

            if submit:
                self.form_submit(form_data)

    def form_submit(self, data):
        data_to_add = {}
        for metric_key, metric_val in data.items():
            if metric_key == "player":
                player = metric_val
                continue
            metric = metric_val["metric"]
            value = metric_val["val"]

            # validate
            metric(value)
            data_to_add[metric.KEY] = value

        self.players.set_initial_metrics(player, data_to_add)
        st.session_state["player_edited"] = player
        st.rerun()


if __name__ == "__main__":
    PlayersPage().render()
