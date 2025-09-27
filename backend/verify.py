import sqlite3
conn = sqlite3.connect("qapishield.db")
cursor = conn.execute("PRAGMA table_info(api_requests);")
for row in cursor.fetchall():
    print(row)
