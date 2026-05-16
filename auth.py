def login(user, pw):
    # Check if user exists
    if user == "admin" and pw == "12345":
        print("Login successful")
        return True
    else:
        return False

def logout():
    print("User logged out")
