
class Compiler:
    """Compile SQL bits"""

    def __init__(self, query, connection):
        self.query = query
        self.connection = connection

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

    def pre_sql_setup(self, bits):
        pass

    def execute(self, sql):
        connection_proxy = self.connection.new_connection()
        try:
            return_values = connection_proxy.get_cursor.execute(sql)
        except Exception as e:
            print(e)
            raise
        else:
            connection_proxy.connection.commit()
            print(list(return_values))
        # connection = self.get_connection()
        # # values = connection.get_cursor.execute(
        # #     "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
        # values = self.get_cursor.execute()
        # print(list(values))
