import json
import os

import streamlit as st


class Login:

    STATE_KEY = "user_hash"
    ENV_USERS_KEY = "USERS"
    ENV_USER_HASH_KEY = "USER_HASH"

    def __init__(self):
        self._get_valid_hashes()

    def _get_valid_hashes(self):
        self.hashes = {}
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
        if Login.STATE_KEY in st.session_state:
            submitted_hash = st.session_state[Login.STATE_KEY]
            if submitted_hash in self.hashes:
                self.user = self.hashes[submitted_hash]
                return True
            else:
                del st.session_state[Login.STATE_KEY]
        return False

    def login(self, hash):
        st.session_state[Login.STATE_KEY] = hash
        if self.check_logged_in():
            st.rerun()
        else:
            st.warning(f"Incorrect login credentials..")

    def get_user(self):
        if self.check_logged_in():
            return self.user
        else:
            raise Exception("Not logged in")
