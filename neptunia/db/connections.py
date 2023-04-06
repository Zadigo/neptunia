from sqlite3 import connect


class Connections:
    def __init__(self):
        from neptunia import PROJECT_PATH
        self.connection = connect(PROJECT_PATH / 'base.sqlite')
        self.cursor = self.connection.cursor
