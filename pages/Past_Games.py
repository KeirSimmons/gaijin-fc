import streamlit as st

from games import Games
from login import Login
from repo import Repo
from stats import Stats
from venues import Venues


class PastGamePage:
    def __init__(self):
        self.login = Login()
        self.login.authentication()

        self.games = Games()
        self.venues = Venues()
        self.stats = Stats()
        self.repo = Repo()

        self.state_checks()
        self.render()

    def state_checks(self):

        if "game-deleted" in st.session_state:
            st.success(f"Game deleted successfully")
            self.repo.commit(f"Deleted game {st.session_state['game-deleted']}")
            del st.session_state["game-deleted"]

    def render(self):
        st.subheader("Past Games")
        games = self.games.get(ongoing=False)

        if not games:
            st.info("No games have been completed yet!")

        for i, game_data in enumerate(games):
            game_key = game_data["key"]
            game = game_data["game"]
            venue = self.venues.get(game["venue"])
            with st.expander(
                f"#{len(games)-i} - **{venue}** {game['date']}", expanded=not i
            ):
                self.stats.process(
                    include_initial=False,
                    games_to_include=[game_key],
                )
                if st.toggle("Delete?", key=f"toggle-delete-game-{game_key}"):
                    if st.button(
                        "Confirm deletion", key=f"confirm-delete-game-{game_key}"
                    ):
                        self.games.del_game(game_key)


if __name__ == "__main__":
    PastGamePage()
