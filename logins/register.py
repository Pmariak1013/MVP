from utils.db import DB
from getpass import getpass
from utils.user_session import session
#from utils.login_utils import hash_password
import bcrypt

def signup():
    DB.connect_admin()

    print("# ------ SIGNUP ------ #")
    while True:
        username = input("Choose a username: ").strip()
        if username == "":
            print("Username cannot be empty. Please try again")
            continue
        
        user_exists, _ = DB.query(query = "SELECT username FROM nba_stats.user WHERE username=%s", connect_type = 'admin', params = (username,))
        if user_exists:
            print("Username already taken. Please try again.")
            continue
        break

    while True:
        pw = getpass("Choose a password: ").strip()
        if pw == "":
            print("Password cannot be empty. Please try again.")
            continue

        confirm = getpass("Confirm password: ").strip()
        if pw != confirm:
            print("Passwords must match.")
            continue
        break

    #hashed = hash_password(pw)
    hashed_password = bcrypt.hashpw(pw.encode('utf-8'), bcrypt.gensalt())
    string_hashed = hashed_password.decode('utf-8')

    privilege_level = 'standard'
    is_active = True
    last_active = "NOW()"

    success = DB.query(query = "INSERT INTO nba_stats.user (username, hashed_password, privilege_level, is_active, last_active) VALUES (%s, %s, %s, %s, %s)", connect_type='admin', params = (username, string_hashed, privilege_level, is_active, last_active))

    print("Signup successful!") if success else print("Signup failed.")

    session.login(username, privilege_level)

    #login_menu()

    DB.close()
    #DB.connect_standard_user()
    return
