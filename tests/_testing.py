# from neptunia.neptunia.db import live_connection
# from neptunia.neptunia.db.compilers import Compiler
# from neptunia.neptunia.db.models import Link, Query
# from neptunia.neptunia.db.sql import Table

# query = Query(Link())
# compiler = Compiler(query, live_connection)

# table = Table('link', compiler=compiler)
# table.model = Link
# # table.create_table()
# table.insert_value()



# # a = table.check_table_exists()
# # b = table.run_sql(a)
# # print(b)

# # compiler = Compiler()
# # print(compiler)
# # values = connection.get_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
# # print(list(values))


from neptunia.neptunia.db.sql import Expression

e = Expression()
print(e.build_select(e.wildcard_all, 'fashion'))
