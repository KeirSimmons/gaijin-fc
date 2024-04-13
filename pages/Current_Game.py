from collections import defaultdict

import streamlit as st

from games import Games
from login import Login
from metrics import Assists, ConcededMetric, DisciplinaryMetric, Goals, MOTMMetric
from players import Players
from repo import Repo
from stats import Stats
from venues import Venues


class CurrentGamePage:
    def __init__(self):
        self.login = Login()
        self.login.authentication()

        self.repo = Repo()
        self.games = Games()
        self.venues = Venues()
        self.players = Players()
        self.stats = Stats()

        self.render()

    def render(self):
        st.subheader("Current Game")

        if "new_game_created" in st.session_state:

            venue = self.venues.get(st.session_state["new_game_created"])

            self.repo.commit(
                (
                    f"Kicking off a new game in {venue}"
                    if venue
                    else "Kicking off a new game"
                ),
            )
            del st.session_state["new_game_created"]

        if "game_completed" in st.session_state:
            st.success(f"Game completed!")
            self.repo.commit(f"Finalising the game after all matches completed")
            del st.session_state["game_completed"]

        if "match_added" in st.session_state:
            self.repo.commit(
                f"Adding scores for a single match (#{st.session_state['match_added']})",
            )
            del st.session_state["match_added"]

        self.ongoing_game = self.games.get(ongoing=True)
        if not len(self.ongoing_game):
            self.render_start_new_game()
        elif len(self.ongoing_game) == 1:
            self.ongoing_game = self.ongoing_game[0]
            self.render_current_game()
        else:
            raise Exception("Multiple ongoing games found")

    def render_current_game(self):

        key = self.ongoing_game["key"]
        game = self.ongoing_game["game"]
        matches_played = len(game["matches"])
        current_match = matches_played + 1

        for match_id, match in enumerate(game["matches"]):
            with st.expander(f"Match {match_id+1}"):
                self.stats.process(
                    include_initial=False,
                    games_to_include=[key],
                    matches_to_include=[match_id],
                )

        form_data = {"players": {}}
        with st.form("add-match", clear_on_submit=True):
            st.markdown(f"**Match {current_match}**")
            with st.expander("Game particulars", expanded=True):
                form_data["level"] = st.selectbox("Level?", ["Enjoy", "Gachi"])
            st.divider()
            for player in self.players.get_data():
                form_data["players"][player] = {}
                with st.expander(player, expanded=True):
                    for metric in [
                        Goals,
                        Assists,
                        ConcededMetric,
                        DisciplinaryMetric,
                        MOTMMetric,
                    ]:
                        key = f"{player}-{metric.KEY}"
                        form_data["players"][player][metric.KEY] = int(
                            metric(val=0, key=key).ask()
                        )
            submit = st.form_submit_button("Submit match")
        if submit:
            self.games.submit_match(form_data)

    def render_start_new_game(self):
        players = self.players.get_data()
        venues = self.venues.get_all()
        venue_map = {venue["name"]: key for key, venue in venues.items()}
        with st.form("new-game"):
            st.markdown("**No ongoing-game - let's start a new one!**")
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
