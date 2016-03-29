import sqlite3

conn = sqlite3.connect("Cookies")

cursor = conn.cursor()

cursor.execute(
    "SELECT host_key FROM cookies LIMIT 10")

result = cursor.fetchall()
# We can also do cursor.fetchone() to fetch individual results from our query

# We can do a conn.commit() or conn.rollback() method on the connection to
# commit or reject changes to a database.

print results

conn.close()
