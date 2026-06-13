def login_user(username, password):
    # Secure SQL execution using parameterized queries
    query = "SELECT * FROM users WHERE username = %s AND password = %s"
    return db.execute(query, (username, password))