
import re
from werkzeug.security import generate_password_hash, check_password_hash

def is_valid_username(username):
    return re.match("^[a-zA-Z0-9_]{3,30}$", username) is not None

def register_user(username, password):
    hashed_password = generate_password_hash(password)
    query = "INSERT INTO users (username, password) VALUES (%s, %s)"
    db.execute(query, (username, hashed_password))

def login_user(username, password):
    if not is_valid_username(username):
        raise ValueError("Invalid username format")
    
    query = "SELECT password FROM users WHERE username = %s"
    result = db.execute(query, (username,))
    if result:
        stored_password = result[0]['password']
        if check_password_hash(stored_password, password):
            return True
    return False
