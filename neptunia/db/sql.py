# from neptunia.neptunia.db import live_connection


import dataclasses
from collections import defaultdict
from neptunia.neptunia.db.connection import Compiler
from neptunia.neptunia.db.models import Link


class Expression:
    select = "SELECT {lhv} FROM {table}"
    create = "CREATE TABLE {table} ({fields})"
    insert = "INSERT INTO {table} ({columns}) VALUES ({values})"
    condition = "WHERE {rhv}"
    join = "AND {rhv}"
    wildcard = "LIKE {rhv}"
    negative_wildcard = "NOT LIKE '{rhv}'"

    def __init__(self, connection=None):
        self.connection = connection
        self.model = None

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.as_sql()}>'

    def as_sql(self):
        return None

    def build_select(self, lhv, table):
        """Build the 'select' sql"""
        return self.select.format(lhv=lhv, table=table)

    def build_join(self, rhv):
        """Build a the join sql e.g. AND"""
        return self.join.format(rhv=rhv)

    def build_params_from_kwargs(self, key, value):
        """Build an sql param using the keyword format
        e.g. type='some value'"""
        return f"{key}='{value}'"

    def build_negative_wildcard(self, rhv):
        """Build the negative wildcard sql e.g. NOT LIKE"""
        return self.negative_wildcard.format(rhv=rhv)

    def build_fields(self, *args):
        """Safely build the fields for an
        sql query e.g. field1,field2"""
        wrong_fields = []
        for value in args:
            if not isinstance(value, str):
                wrong_fields.append(value)
        if wrong_fields:
            raise
        return ','.join(args)

    def cast_field_to_type(self, name, field_type):
        default_type = 'TEXT'
        if field_type == int:
            default_type = 'INTEGER'
        return f'{name} {default_type}'

    def set_field_options(self, value, unique=False, not_null=False):
        if not_null:
            value = f'{value} NOT NULL'

        if unique:
            value = f'{value} UNIQUE'
        return value

    def primary_key_sql(self, value):
        return f'{value} PRIMARY KEY'


class Where(Expression):
    def __init__(self, rhv):
        super().__init__()
        self.rhv = rhv

    def as_sql(self):
        return self.condition.format(rhv=self.rhv)


class And(Expression):
    def __init__(self, rhv):
        self.rhv = rhv

    def as_sql(self):
        return self.build_join(rhv=self.rhv)


class Table(Expression):
    def __init__(self, table_name, connection=None):
        super().__init__()

        if connection is not None:
            self.connection = connection

        self.table_name = table_name
        self.main_table_name = 'sqlite_master'
        self.model_fields = defaultdict(set)
        self.fields_map = {}

    def check_table_exists_sql(self):
        """Outputs the sql to check if a table 
        exist in the database"""
        fields = self.build_fields('name')
        select = self.build_select(fields, self.main_table_name)
        where_object = Where(self.build_params_from_kwargs('type', 'table'))
        and_object = And(self.build_fields('name'))
        bits = (
            select,
            where_object,
            and_object,
            self.build_negative_wildcard('sqlite_%')
        )
        return self.connection.compile(bits)

    def check_table_exists(self):
        """Checks if a table exists in the database"""
        tables = self.connection.execute(self.check_table_exists_sql())
        return self.table_name in tables

    def create_table(self):
        """Creates a table in the database"""
        model_name = getattr(self.model, '__name__', None)
        self.table_name = model_name.lower()
        fields = self.model_fields[self.model]
        if not fields:
            field_objects = dataclasses.fields(Link)
            for field in field_objects:
                fields.add(field.name)
                self.fields_map[field.name] = field.type
            self.model_fields[self.model].update(fields)

        true_fields = []
        for name, field_type in self.fields_map.items():
            result = self.cast_field_to_type(name, field_type)
            if name == 'id':
                result = self.primary_key_sql(result)
            true_fields.append(result)
        sql_fields = self.build_fields(*list(true_fields))
        sql = self.create.format(table=self.table_name, fields=sql_fields)
        final_sql = self.connection.compile([sql])
        self.connection.execute(final_sql)
        print(true_fields)

    def delete_table(self):
        """Deletes a table from the database"""

    def insert_value(self):
        """Inserts an item in the database"""

    def delete_value(self):
        pass

    def update_value(self):
        pass


live_connection = Compiler()

table = Table('mytable', connection=live_connection)
table.model = Link
table.create_table()

# a = table.check_table_exists()
# b = table.run_sql(a)
# print(b)

# compiler = Compiler()
# print(compiler)
# values = connection.get_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
# print(list(values))


Link.objects.all()
