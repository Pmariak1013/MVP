from utils.db import DB
from utils.user_session import session
from utils.login_utils import user_activity_timeout

def logout():
    if not session.logged_in:
        print("No user logged in.")
        return
    
    elif session.user == 'admin' and session.privilege == 1:
        print("Logging out admin user.\n")
        session.logged_in = False
        session.user = None
        session.privilege = 0
        session.player_selected_state = False
        session.player_selected_name = (None, None)
        session.last_active = None
        return True
    

    username = session.user


    # set the user's is_active to False since they are logged out now
    success = DB.query(query = "UPDATE nba_stats.user SET is_active=False, last_active=NOW() WHERE username=%s", connect_type = 'admin', params = (username,))

    print(f"Logged out {session.user}!") if success else print("Log out failed.\n")

    # close DB connection.
    DB.close()

    session.logout()
    return True