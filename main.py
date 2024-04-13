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

        self.stats = Stats()
        self.show_summary()
        self.show_commit_button()

    def show_summary(self):
        self.stats.process()
        Promotions(self.stats.get_points()).display_progress_bar()

    def show_commit_button(self):
        repo = Repo()
        if repo.find_changes():
            if st.button("Save changes?"):
                repo.commit(auto=False)


if __name__ == "__main__":
    Main()
