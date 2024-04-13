import streamlit as st

from login import Login
from venues import Venues


class VenuesPage:
    def __init__(self):
        self.login = Login()
        self.login.authentication()

        self.venues = Venues()
        self.render()

    def render(self):
        st.subheader("Venues")
        if "venue-added" in st.session_state:
            st.success(f"New venue added ({st.session_state['venue-added']})")
            del st.session_state["venue-added"]
        self.render_edit_form()
        self.render_add_form()

    def render_edit_form(self):
        venues = self.venues.get_all()
        venue_map = {venue["name"]: key for key, venue in venues.items()}

        if venue_map:

            venue_to_edit = st.selectbox("Venue", options=venue_map.keys())

            if venue_to_edit:
                key = venue_map[venue_to_edit]

                with st.form(f"venue-edit-{key}"):
                    new_name = st.text_input("Venue name", value=venue_to_edit)
                    submit = st.form_submit_button("Edit")
                with st.expander("Delete venue?", expanded=False):
                    delete = st.button("Confirm")

            if submit:
                self.venues.edit(key, {"name": new_name})

            if delete:
                self.venues.delete(key)

        else:
            st.info("No venues to display.")

    def render_add_form(self):
        st.divider()
        with st.expander("Add a new venue?", expanded=False):
            with st.form("add-venue"):
                name = st.text_input("Venue name?")
                submit = st.form_submit_button("Add venue")
            if submit:
                self.venues.add({"name": name})


if __name__ == "__main__":
    VenuesPage()
