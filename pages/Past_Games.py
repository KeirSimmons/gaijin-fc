import streamlit as st

from games import Games
from login import Login
from venues import Venues


class PastGamePage:
    def __init__(self):
        self.login = Login()
        self.login.authentication()

        self.games = Games()
        self.venues = Venues()
        self.render()

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
                st.write(game)


if __name__ == "__main__":
    PastGamePage()
