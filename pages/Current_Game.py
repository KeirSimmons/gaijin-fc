from collections import defaultdict

import streamlit as st

from games import Games
from metrics import Assists, Goals
from players import Players
from venues import Venues


class CurrentGamePage:
    def __init__(self):
        self.games = Games()
        self.venues = Venues()
        self.players = Players()

        self.render()

    def render(self):
        st.subheader("Current Game")
        self.ongoing_game = self.games.get(ongoing=True)
        if not len(self.ongoing_game):
            self.report_completed_game()
            self.render_start_new_game()
        elif len(self.ongoing_game) == 1:
            self.ongoing_game = self.ongoing_game[0]
            self.render_current_game()
        else:
            raise Exception("Multiple ongoing games found")

    def report_completed_game(self):
        if "game_completed" in st.session_state:
            st.info(f"Game completed! ")
            del st.session_state["game_completed"]

    def render_current_game(self):

        key = self.ongoing_game["key"]
        game = self.ongoing_game["game"]

        for i, match in enumerate(game["matches"]):
            with st.expander(f"Match {i+1}"):
                st.write(match)

        form_data = {"players": {}}
        with st.form("something"):
            for player in self.players.get_data():
                form_data["players"][player] = {}
                with st.expander(player, expanded=True):
                    for metric in [Goals, Assists]:
                        form_data["players"][player][metric.KEY] = st.number_input(
                            metric.MATCH_LABEL,
                            key=f"{player}-{metric.KEY}",
                            step=1,
                        )
            with st.expander("Game particulars", expanded=True):
                form_data["level"] = st.selectbox("Level?", ["Enjoy", "Gachi"])
            submit = st.form_submit_button("Submit match")
        if submit:
            self.games.submit_match(form_data)

    def render_start_new_game(self):
        players = self.players.get_data()
        venues = self.venues.get_all()
        venue_map = {venue["name"]: key for key, venue in venues.items()}
        with st.form("new-game"):
            form_data = {
                "date": st.date_input("Date?", format="YYYY/MM/DD"),
                "venue": st.selectbox(
                    "Where?",
                    [self.venues.get(venue) for venue in venues],
                ),
                "players": st.multiselect(
                    "Who's playing?",
                    options=list(players.keys()),
                    default=list(players.keys()),
                ),
                "no_of_matches": st.number_input(
                    "No. of matches (total):", value=8, min_value=1, step=1
                ),
                "duration": st.number_input(
                    "Time per match (mins)", value=7, min_value=1, step=1
                ),
            }
            submit = st.form_submit_button("Start game!")
        if submit:
            form_data["venue"] = venue_map[form_data["venue"]]
            self.create_game(form_data)

    def create_game(self, form_data):
        form_data["date"] = str(form_data["date"])
        self.games.add_game(form_data)


if __name__ == "__main__":
    CurrentGamePage()
