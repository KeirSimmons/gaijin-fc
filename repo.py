import base64
import os

import streamlit as st
from github import Auth, Github, InputGitTreeElement

from login import Login


class Repo:
    REPO_NAME = "gaijin-fc"
    AUTH_TOKEN_KEY = "GITHUB_AUTH_TOKEN"
    AUTO_COMMIT_KEY = "AUTO_COMMIT"

    def __init__(self):
        self.login = Login()
        self.login.authentication(render=False)

        self.load_secret()
        self.connect()
        self.find_files()

    def load_secret(self):
        if Repo.AUTH_TOKEN_KEY in os.environ:
            self.auth_token = os.environ[Repo.AUTH_TOKEN_KEY]
        else:
            st.exception("Environment authentication key not set.")

    def connect(self):
        auth = Auth.Token(self.auth_token)
        g = Github(auth=auth)
        self.repo = g.get_user().get_repo(Repo.REPO_NAME)
        if self.repo.name != Repo.REPO_NAME:
            st.exception("Incorrect repo loaded")

    def find_files(self):
        files = []
        for fh in os.listdir("."):
            if fh.endswith(".json"):
                files.append(fh)
        self.files = files

    def commit(self, msg=None, auto=True):
        if auto and os.environ[Repo.AUTO_COMMIT_KEY] != 1:
            # Don't commit if this is an auto commit and setting is off
            return None
        with st.spinner(text="Committing all changes.."):
            repo = self.repo
            username = self.login.get_user()

            if msg is None:
                commit_message = f"{username}: Automated commit from app interaction"
            else:
                commit_message = f"{username}: {msg} (Automated commit)"
            master_ref = repo.get_git_ref("heads/main")
            master_sha = master_ref.object.sha
            base_tree = repo.get_git_tree(master_sha)

            element_list = list()
            for i, entry in enumerate(self.files):
                with open(entry) as input_file:
                    data = input_file.read()
                if entry.endswith(".png"):  # images must be encoded
                    data = base64.b64encode(data)
                github_file = repo.get_contents(entry)
                github_content = github_file.decoded_content.decode("utf-8")
                if github_content != data:
                    st.info(f"Committing changes to file {entry}")
                    element = InputGitTreeElement(self.files[i], "100644", "blob", data)
                    element_list.append(element)

            if element_list:
                tree = repo.create_git_tree(element_list, base_tree)
                parent = repo.get_git_commit(master_sha)
                commit = repo.create_git_commit(commit_message, tree, [parent])
                master_ref.edit(commit.sha)
                st.info("All changes committed")
            else:
                st.info("No changes to commit")


if __name__ == "__main__":
    Repo()
