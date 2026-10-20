from utils.db import DB
from utils.user_session import session
#from utils.login_utils import hash_password
import bcrypt
from getpass import getpass 

def delete_account():
    
    print("# ------ Delete Account ------ #")
    while True:
        username = input("Username: ").strip()

        query = "SELECT * FROM nba_stats.user WHERE username = %s"

        result, _ = DB.query(query = query, connect_type = 'admin', params = (username, ))

        if not result or len(result[0]) == 0:
            print("Invalid username. Please try again.")
            continue
        break

    print("\nWARNING: This action cannot be undone!")
    confirm = getpass(f"Enter password to confirm account deletion: ").strip()

    if confirm == "":
        print("Password cannot be empty.")
        DB.close()
        return
    

    hashed_pw = result[0][2].encode('utf-8')

    if not bcrypt.checkpw(confirm.encode('utf-8'), hashed_pw):
        DB.close()
        print("\nIncorrect password.\n\n")
        #print(f'{"=" * 55}\n')
        return False

    
    #result, _ = DB.query("SELECT username FROM users where username=%s and password_hash=%s",(username,confirm))
    #if not result:
    #    print("Password incorrect. Account not deleted.")
    #    DB.close()
    #    return
    


    
    success = DB.query(query = "DELETE FROM nba_stats.user WHERE username = %s", connect_type = 'admin', params = (username,))
    print("Account successfully deleted.") if success else print("Account deletion failed.")
    if session.user == username:
        session.logout()
    DB.close()