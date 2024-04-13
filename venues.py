import json

import streamlit as st

from games import Games


class Venues:

    FILE = "./venues.json"

    def __init__(self):
        self.load()
        self.games = Games()

    def load(self):
        with open(Venues.FILE) as file:
            self.data = json.load(file)

    def save(self):
        with open(Venues.FILE, "w") as file:
            json.dump(self.data, file, indent=4, sort_keys=True)

    def get_all(self):
        return self.data

    def get(self, key):
        return self.data.get(key)["name"]

    def get_key(self, venue):
        return [key for key, data in self.get_all().items() if data["name"] == venue][0]

    def edit(self, key, new_data):
        if key in self.data:
            old_venue_name = self.data[key]["name"]
            self.data[key].update(new_data)
            new_venue_name = self.data[key]["name"]
            self.save()
            st.session_state["venue-edited"] = f"{old_venue_name} -> {new_venue_name}"
            st.rerun()
        else:
            raise Exception(f"Venue does not exist.")

    def delete(self, key):
        if key in self.data:
            games = self.games.get()
            venues = set([game["game"]["venue"] for game in games])
            if key in venues:
                raise Exception("Cannot delete venue as it has been played at before.")
            else:
                venue_name = self.data[key]["name"]
                del self.data[key]
                st.session_state["venue-deleted"] = venue_name
            self.save()
            st.rerun()
        else:
            raise Exception(f"Venue does not exist.")

    def add(self, data):
        try:
            self.get_key(data["name"])
            exists = True
        except IndexError:
            # Doesn't exist (good!)
            exists = False
        if not exists:
            key = self.generate_key()
            self.data[key] = data
            self.save()
            st.session_state["venue-added"] = data["name"]
            st.rerun()
        else:
            st.warning("Venue already exists.")

    def generate_key(self):
        # Format: venue-xx
        recent_ids = sorted(
            [int(x.split("-")[1]) for x in self.data.keys()], reverse=True
        )
        most_recent_id = recent_ids[0] if len(recent_ids) else 0
        return f"venue-{most_recent_id+1}"
