import sqlite3
from functools import cached_property

# import string


class BaseConnection:
    """Creates a proxy for a 
    database connection"""

    def __init__(self):
        self.connection = None

    def __str__(self):
        return f'<{self.__class__.__name__}: ready: {self.is_ready}>'

    def __quit__(self):
        self.connection.close()

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
        return cls()

    @property
    def is_ready(self):
        return self.connection is not None


class SQLiteConnection(BaseConnection):
    """Creates a base SQLite connection"""

    def __init__(self):
        super().__init__()
        self.connection = sqlite3.connect('db.sqlite')


class Compiler:
    """Compile SQL bits"""
    connection = SQLiteConnection

    def _compile_bits(self, bits):
        for bit in bits:
            if isinstance(bit, str):
                yield str(bit).strip()
            else:
                yield bit.as_sql()

    def _normalize_structure(self, sql):
        if not sql.endswith(';'):
            return f'{sql};'
        return sql

    def construct_sql(self, clean_bits):
        return ' '.join(clean_bits)

    def compile(self, sql_bits):
        self.pre_sql_setup(sql_bits)
        bits = list(self._compile_bits(sql_bits))
        sql = self.construct_sql(bits)
        return self._normalize_structure(sql)

    def get_connection(self):
        return self.connection()

    def pre_sql_setup(self, bits):
        pass

    def execute(self, sql):
        connection_proxy = self.connection.new_connection()
        try:
            return_values = connection_proxy.get_cursor.execute(sql)
        except Exception as e:
            raise
        else:
            print(list(return_values))

        # connection = self.get_connection()
        # # values = connection.get_cursor.execute(
        # #     "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        # values = self.get_cursor.execute()
        # print(list(values))


# c = Compiler()
# print(c.connection.new_connection())
