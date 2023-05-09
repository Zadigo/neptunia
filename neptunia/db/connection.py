import sqlite3
from functools import cached_property


class Expression:
    select = "SELECT {lhv} FROM {table}"
    create = "CREATE {table} ({fields})"
    insert = "INSERT INTO {table} ({columns}) VALUES ({values})"
    condition = "WHERE {rhv}"
    join = "AND {rhv}"
    negative_wildcard = "NOT LIKE '{rhv}'"

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.as_sql()}>'
    
    def as_sql(self):
        return None

    def build_select(self, lhv, table):
        return self.select.format(lhv=lhv, table=table)
    
    def build_join(self, rhv):
        return self.join.format(rhv=rhv)
    
    def build_params_from_kwargs(self, key, value):
        return f"{key}='{value}'"
    
    def build_negative_wildcard(self, rhv):
        return self.negative_wildcard.format(rhv=rhv)
    
    def build_fields(self, *args):
        wrong_fields = []
        for value in args:
            if not isinstance(value, str):
                wrong_fields.append(value)
        if wrong_fields:
            raise
        return ','.join(args)
    
    def finalize(self, items):
        pass

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
    def __init__(self, table_name):
        self.table_name = table_name
        self.main_table_name = 'sqlite_master'

    def check_table_exists(self, compiler):
        fields = self.build_fields('name')
        select = self.build_select(fields, self.main_table_name)
        where_object = Where(self.build_params_from_kwargs('type', 'table'))
        and_object = And(self.build_fields('name'))
        bits = select, where_object, and_object, self.build_negative_wildcard('sqlite_%')
        return compiler.compile(bits)

    def as_sql(self):
        select = self.build_select('name', self.table_name)
        return select




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

    def execute(self):
        connection = self.get_connection()
        # values = connection.get_cursor.execute(
        #     "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        values = self.get_cursor.execute()
        print(list(values))

compiler = Compiler()

table = Table('mytable')
print(table.check_table_exists(compiler))

# compiler = Compiler()
# print(compiler)
# values = connection.get_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
# print(list(values))
