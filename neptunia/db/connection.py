import sqlite3
from functools import cached_property

class Expression:
    select = 'SELECT {lhv} FROM {table}'
    create = 'CREATE {table} ({fields})'
    insert = 'INSERT INTO {table} ({columns}) VALUES ({values})'
    condition = '{lhv} WHERE {rhv}'
    join = '{lhv} AND {rhv}'
    negative_wildcard = '{lhv} NOT LIKE {rhv}'
    
    def as_sql(self):
        pass


class Table(Expression):
    def __init__(self, table_name):
        self.table_name = table_name

    def as_sql(self):
        select = self.select.format(lhv='name', table=self.table_name)
        return select


class Where(Expression):
    def as_sql(self):
        pass

class BaseConnection:
    def __init__(self):
        self.connection = sqlite3.connect('db.sqlite')

    @cached_property
    def get_connection(self):
        return self.connection

    @cached_property
    def get_cursor(self):
        return self.get_connection.cursor()


class Compiler:
    connection = BaseConnection

    def get_connection(self):
        return self.connection()

    def pre_sql_setup(self):
        pass

    def build_sql(self):
        table =  Table('sqlite_master')

    def execute(self):
        connection = self.get_connection()
        values = connection.get_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        print(list(values))

        
compiler = Compiler()
compiler.execute()
# values = connection.get_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
# print(list(values))