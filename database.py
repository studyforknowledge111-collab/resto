import sqlite3

conn = sqlite3.connect('database.db')

conn.execute('''
CREATE TABLE IF NOT EXISTS orders(
id INTEGER PRIMARY KEY AUTOINCREMENT,
table_id INTEGER,
food TEXT,
qty INTEGER,
status TEXT,
payment TEXT
)
''')

print("Database Ready Successfully!")

conn.close()