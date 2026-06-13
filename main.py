
import re
from werkzeug.security import generate_password_hash, check_password_hash

def is_valid_username(username):
    # Example: Usernames must be alphanumeric and 3-20 characters long
    return re.match(r'^[a-zA-Z0-9]{3,20}$', username) is not None

def register_user(username, password):
    # Hash the password before storing it
    hashed_password = generate_password_hash(password)
    query = "INSERT INTO users (username, password) VALUES (%s, %s)"
    db.execute(query, (username, hashed_password))

def login_user(username, password):
    if not is_valid_username(username):
        raise ValueError("Invalid username format")
    query = "SELECT * FROM users WHERE username = %s"
    user = db.execute(query, (username,))
    if user and check_password_hash(user['password'], password):
        return user
    return None
