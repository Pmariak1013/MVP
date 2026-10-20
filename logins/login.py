from utils.db import DB
from getpass import getpass 
from utils.user_session import session
import logging
#from utils.login_utils import hash_password
import bcrypt

def login():
    #DB.connect()
    print("# ------ LOGIN ------ #")
    username = input("Username: ").strip()
    pw = getpass("Password: ").strip()
    #hashed = hash_password(pw)

    rows, _ = DB.query(query = "SELECT username, privilege_level, hashed_password FROM nba_stats.user WHERE username = %s", connect_type = "standard_user", params = (username,))

    if not rows:
        logging.debug(f'\n\n\n[DEBUG]:  No rows returned for username={username}\n\n\n')
        DB.close()
        print("\nInvalid username or password.\n\n")
        #print(f'{"=" * 55}\n')
        return False
    
    hashed_pw = rows[0][2].encode('utf-8')

    if not bcrypt.checkpw(pw.encode('utf-8'), hashed_pw):
        DB.close()
        print("\nInvalid username or password.\n\n")
        #print(f'{"=" * 55}\n')
        return False

    privilege = rows[0][1]

    session.login(user = username, priv = privilege)

    DB.query(query = "UPDATE nba_stats.user SET is_active = True, last_active = NOW() WHERE username=%s", connect_type = "admin", params = (username,))
    print(f"Welcome back, {username}!\n\n")
    #print(f'{"=" * 55}\n')

    logging.debug(f'\n\n\n[DEBUG]:  Successful login for username={username} with privilege_level={privilege}, now closing connection\n\n\n')
    DB.close()
    return True