
import sqlite3

def login_user(username, password):
    # Secure SQL execution using parameterized queries
    query = "SELECT * FROM users WHERE username = ? AND password = ?"
    # Assuming `db` is a connection object
    cursor = db.cursor()
    cursor.execute(query, (username, password))
    return cursor.fetchall()
