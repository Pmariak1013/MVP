from utils.db import DB
from utils.user_session import session
from datetime import datetime, timedelta
import hashlib
import logging

#def hash_password(pw):
#    return hashlib.sha256(pw.encode()).hexdigest()

def refresh_activity(user):
    logging.debug(f'\n\n\n[DEBUG] (login_utils.py):  refresh_activity called for user={user}\n\n\n')
    session.refresh_activity()


    logging.debug(f'\n\n\n[DEBUG] (login_utils.py):  attempting to access DB to update last_active for user={user}\n\n\n')

    if user is None:
        logging.debug(f'\n\n\n[DEBUG] (login_utils.py):  No user logged in, skipping DB update\n\n\n')
        return
    
    if session.user == 'admin' and session.privilege == 1:
        logging.debug(f'\n\n\n[DEBUG] (login_utils.py):  Admin user logged in, skipping DB update\n\n\n')
        session.last_active = datetime.now()
        return

    #if DB.conn is None:
    #    DB.connect_admin()
    #else:
    #    DB.close()
    #    DB.connect_admin()

    DB.query(query = "UPDATE nba_stats.user SET last_active=NOW() where username=%s", connect_type = "admin", params = (user,)) # type: ignore






def user_activity_timeout(user):
    logging.debug(f'\n\n\n[DEBUG (login_utils.py)]:  user_activity_timeout called for user={user}\n\n\n')

    if session.user == 'admin' and session.privilege == 1 and session.user_activity_timeout():
        logging.debug(f'\n\n\n[DEBUG] (login_utils.py):  Admin user logged in, execute timeout on python side\n\n\n')
        session.user = None
        session.privilege = 0
        session.logged_in = False
        session.last_active = None
        return True
    
    elif session.user == 'admin' and session.privilege == 1 and session.user_activity_timeout() is False:
        logging.debug(f'\n\n\n[DEBUG] (login_utils.py):  Admin user logged in, skipping timeout\n\n\n')
        return False

    if session.user_activity_timeout():
        logging.debug(f'\n\n\n[DEBUG (login_utils.py)]:  user_activity_timeout triggered for user={user}\n\n\n')
        DB.query(query = "UPDATE nba_stats.user SET is_active=FALSE where username=%s", connect_type = "admin", params = (user,))
        session.logout()
        return True
    



    logging.debug(f'\n\n\n[DEBUG (login_utils.py)]:  querying last_active for user={user}\n\n\n')
    result, _ = DB.query(query = "SELECT last_active FROM nba_stats.user WHERE username=%s", connect_type = "standard_user", params = (user,))
    if result is False:
        return True
    




    last_login = result[0][0]
    if datetime.now() - last_login > timedelta(minutes=5):
        logging.debug(f'\n\n\n[DEBUG (login_utils.py)]:  inactivity timeout exceeded for user={user}\n\n\n')
        DB.query(query = "UPDATE nba_stats.user SET is_active=FALSE where username=%s", connect_type = "admin", params = (user,))
        session.logout()
        return True
    return False 




def get_privilege_level(user):
    logging.debug(f'\n\n\n[DEBUG] (login_utils.py):  get_privilege_level called for user={user}\n\n\n')

    if session.user == 'admin' and session.privilege == 1:
        logging.debug(f'\n\n\n[DEBUG] (login_utils.py):  Admin user logged in, skipping DB update\n\n\n')
        return



    result, _ = DB.query(query = "SELECT privilege_level FROM nba_stats.user WHERE username=%s", connect_type = "standard_user", params = (user,))
    
    
    if result is False:
        return None
    

    return result[0][0]




def logoutAllUsers():
    logging.debug(f'\n\n\n[DEBUG] (login_utils.py):  logoutAllUsers called\n\n\n')

    DB.query(query = "UPDATE nba_stats.user SET is_active=FALSE", connect_type = "admin")
    DB.close()
    return