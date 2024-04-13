from login import Login


class Logout:

    def __init__(self):
        self.login = Login()

    def process(self):
        self.login.logout()


if __name__ == "__main__":
    Logout().process()
