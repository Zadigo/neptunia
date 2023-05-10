import sqlite3
from functools import cached_property

# import string

# Keep track of all concurrent 
# database connections
CONNECTIONS_CACHE = set()


class BaseConnection:
    """Creates a proxy for a 
    database connection"""

    def __init__(self):
        self.connection = None
        CONNECTIONS_CACHE.add(self)

    def __repr__(self):
        return f'<{self.__class__.__name__}: ready: {self.is_ready}>'

    def __quit__(self):
        print('closed connections', CONNECTIONS_CACHE)
        self.disconnect()

    @cached_property
    def get_connection(self):
        return self.connection

    @cached_property
    def get_cursor(self):
        return self.get_connection.cursor()

    @classmethod
    def new_connection(cls):
        """Returns a new connection precisely
        for the current SQL to execute"""
        instance = cls()
        CONNECTIONS_CACHE.add(instance)
        return instance

    @property
    def is_ready(self):
        return self.connection is not None
    
    def disconnect(self):
        self.connection.close()

    def disconnect_all(self):
        for connection in CONNECTIONS_CACHE:
            connection.disconnect()


class SQLiteConnection(BaseConnection):
    """Creates a base SQLite connection"""

    def __init__(self):
        super().__init__()
        self.connection = sqlite3.connect('db.sqlite')
        print('connections', CONNECTIONS_CACHE)
