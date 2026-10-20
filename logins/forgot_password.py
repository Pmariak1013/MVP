from utils.db import DB
from getpass import getpass 
#from utils.login_utils import hash_password

def forgot_password():
    DB.connect_admin()
    print("# ------ PASSWORD RESET ------ #")
    while True:
        username = input("Username: ").strip()
        result, _ = DB.query("SELECT username FROM users where username = %s", (username,))

        if not result:
            print("Invalid username. Please try again.")
            continue

        old_pass = getpass("Old password: ").strip()
        hashed = hash_password(old_pass)
        result, _ = DB.query("SELECT username FROM users where username=%s AND password_hash=%s",(username,hashed))
        if not result:
            print("Incorrect password")
            DB.close()
            return

        new_pass = getpass("New password: ").strip()
        if new_pass == "":
                print("Password cannot be empty. Please try again.")
                continue
        
        confirm = getpass("Confirm password: ").strip()
        if new_pass != confirm:
            print("Passwords must match.")
            continue
        break

    hashed = hash_password(new_pass)
    success = DB.query("UPDATE users SET password_hash=%s WHERE username=%s",(hashed,username))
    print(f"Password changed for {username}!") if success else print("Could not change password.")
    DB.close()  