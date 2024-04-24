import json

import streamlit as st


class Promotions:
    FILE = "./promotions.json"
    POINTS_KEY = "points"
    TEAM_KEY = "team"

    def __init__(self, points):

        self.points = points

        self.load()
        self.crunch()

    def load(self):
        self._has_changes = False
        with open(Promotions.FILE) as file:
            self.data = json.load(file)

    def save(self):
        with open(Promotions.FILE, "w") as file:
            json.dump(self.data, file, indent=4, sort_keys=True)

    def crunch(self):
        self.current = None
        self.next = None
        for team_data in self.data:
            if self.points >= team_data[Promotions.POINTS_KEY]:
                self.current = team_data
            else:
                self.next = team_data
                break

    def get_current(self):
        if self.current is not None:
            return self.current
        else:
            st.warning("We could not place you into a team.")

    def get_next(self):
        if self.next is not None:
            return self.next
        else:
            st.warning("There are no more teams to promote you to!")

    def get_progress(self):
        """Progress % to the next promotion level"""

        if self.next is None or self.current is None:
            return None

        zero_level = self.current[Promotions.POINTS_KEY]
        max_level = self.next[Promotions.POINTS_KEY]

        progress = (self.points - zero_level) / (max_level - zero_level)
        return progress

    def display_progress_bar(self):
        next_point_rqmnt = self.get_next()[Promotions.POINTS_KEY]
        progress = self.get_progress()
        st.progress(
            progress,
            text=f"{self.points} / {next_point_rqmnt} points",
        )
