import json
import os

import extra_streamlit_components as stx
import streamlit as st


@st.cache_resource(experimental_allow_widgets=True)
def get_manager():
    return stx.CookieManager()


class Login:

    STATE_KEY = "user_hash"
    ENV_USERS_KEY = "USERS"
    ENV_USER_HASH_KEY = "USER_HASH"

    def __init__(self):
        self._get_valid_hashes()
        self.cookie_manager = get_manager()

    def _get_valid_hashes(self):
        self.hashes = {}
        if (
            Login.ENV_USER_HASH_KEY not in os.environ
            or Login.ENV_USERS_KEY not in os.environ
        ):
            raise Exception("Required environment variables not set.")
        users = json.loads(os.environ[Login.ENV_USERS_KEY])
        hashes = json.loads(os.environ[Login.ENV_USER_HASH_KEY])
        for user, hash in zip(users, hashes):
            self.hashes[hash] = user

    def authentication(self, render=True):
        if self.check_logged_in():
            # Can do something with self.user
            pass
        elif render:
            st.header("Login")
            with st.form("login-form"):
                hash = st.text_input("Enter your birthday", placeholder="DDMMYYYY")
                submit = st.form_submit_button("Login")

            if submit:
                self.login(hash)
            st.stop()
        else:
            raise Exception("Cannot process as not logged in.")

    def check_logged_in(self):
        submitted_hash = str(self.cookie_manager.get(Login.STATE_KEY))
        if submitted_hash in self.hashes:
            self.user = self.hashes[submitted_hash]
            return True
        return False

    def login(self, hash):
        self.cookie_manager.set(Login.STATE_KEY, hash)
        if self.check_logged_in():
            st.rerun()
        else:
            st.warning(f"Incorrect login credentials..")

    def get_user(self):
        if self.check_logged_in():
            return self.user
        else:
            raise Exception("Not logged in")

    def logout(self):
        if self.check_logged_in():
            self.cookie_manager.delete(Login.STATE_KEY)
        st.switch_page("main.py")
