import json
import time

import streamlit as st


class Games:

    FILE = "./games.json"

    def __init__(self):
        self.load()

    def load(self):
        self._has_changes = False
        with open(Games.FILE) as file:
            self.data = json.load(file)

    def save(self):
        with open(Games.FILE, "w") as file:
            json.dump(self.data, file, indent=4, sort_keys=True)

    def get(self, ongoing=None):
        games = [
            {"key": key, "game": game}
            for key, game in self.data.items()
            if (ongoing is None or game["ongoing"] is ongoing)
        ]
        # Show most recent games first
        games = sorted(games, key=lambda x: x["game"]["created"], reverse=True)
        return games

    def add_game(self, data):
        # No validation
        game_key = self.generate_key()
        data["ongoing"] = True
        data["created"] = time.time()
        data["matches"] = []
        self.data[game_key] = data
        self.save()
        st.session_state["new_game_created"] = data["venue"]
        st.rerun()

    def del_game(self, game_key):
        if game_key in self.data:
            del self.data[game_key]
            self.save()
            st.session_state["game-deleted"] = game_key
            st.rerun()

    def del_match(self, game_key, match_id):
        if game_key in self.data and (
            len(self.data[game_key]["matches"]) == match_id + 1
        ):
            self.data[game_key]["matches"] = self.data[game_key]["matches"][:-1]
            self.save()
            st.session_state["match-deleted"] = f"game {game_key}, match {match_id}"
            st.rerun()

    def generate_key(self):
        # Format: game-xx
        recent_ids = sorted(
            [int(x.split("-")[1]) for x in self.data.keys()], reverse=True
        )
        most_recent_id = recent_ids[0] if len(recent_ids) else 0
        return f"game-{most_recent_id+1}"

    def submit_match(self, data):
        # No validation on input, just # of matches
        ongoing = self.get(ongoing=True)
        if len(ongoing) != 1:
            raise Exception("Expected 1 ongoing game.")
        game_data = ongoing[0]
        game_key = game_data["key"]
        game = game_data["game"]
        matches = len(game["matches"])
        max_no_of_matches = game["no_of_matches"]
        if matches >= max_no_of_matches:
            raise Exception(f"Already reached max of {max_no_of_matches} matches.")
        game["matches"].append(data)
        if matches + 1 == max_no_of_matches:
            st.session_state["game_completed"] = game_key
            game["ongoing"] = False
        else:
            st.session_state["match_added"] = f"{matches+1}/{max_no_of_matches}"
        self.data[game_key] = game
        self.save()
        st.rerun()
