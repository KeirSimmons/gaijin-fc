import streamlit as st

from login import Login
from promotions import Promotions
from repo import Repo
from stats import Stats


class Main:

    def __init__(self):
        st.set_page_config(page_title="Main")
        self.login = Login()
        self.login.authentication()

        st.header("Gaijin FC")

        self.stats = Stats()
        self.show_summary()
        self.show_commit_button()

        st.divider()
        st.markdown(f"_Logged in as {self.login.get_user()}_")

    def show_summary(self):
        normalise = st.session_state.get("normalise_graph") or False
        remove = {
            "celtic": st.session_state.get("graph_celtic") or False,
            "rangers": st.session_state.get("graph_rangers") or False,
        }
        self.stats.process(
            normalise=normalise,
            include_new=not remove["rangers"],
            include_initial=not remove["celtic"],
        )
        st.markdown("**Points till next promotion!**")
        Promotions(self.stats.get_points()).display_progress_bar()

        st.session_state["normalise_graph"] = st.toggle("Normalise?")
        st.session_state["graph_celtic"] = st.toggle("Remove Celtic games?")
        st.session_state["graph_rangers"] = st.toggle("Remove Rangers games?")
        if (
            (normalise is not st.session_state.get("normalise_graph"))
            or (remove["celtic"] is not st.session_state["graph_celtic"])
            or (remove["rangers"] is not st.session_state["graph_rangers"])
        ):
            st.rerun()

    def show_commit_button(self):
        repo = Repo()
        if repo.find_changes():
            if st.button("Save changes?"):
                repo.commit(auto=False)


if __name__ == "__main__":
    Main()
