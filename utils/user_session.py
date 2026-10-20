from datetime import datetime, timedelta
import logging

class Session:
    def __init__(self):
        self.user = None
        self.privilege = 0
        self.logged_in = False
        self.last_active = None
        self.player_selected_state = False
        self.player_selected_name = (None, None)  # (first_name, last_name)
        self.team_selected_name = None



    def login(self,user,priv):
        self.user = user
        self.privilege = priv
        self.logged_in = True
        self.last_active = datetime.now()



    def logout(self):
        logging.debug(f'\n\n\n[DEBUG] (user_session.py):  logout called \n\n')
        self.user = None
        self.privilege = 0
        self.logged_in = False
        self.last_active = None
        self.player_selected_name = (None, None)
        self.player_selected_state = False






    def refresh_activity(self):
        logging.debug(f'\n\n\n[DEBUG] (user_session.py):  refresh_activity called for user={self.user}\n\n\n')


        if self.logged_in:
            logging.debug(f'\n\n\n[DEBUG] (user_session.py):  user {self.user} is logged in, updating last_active\n\n\n')
            self.last_active = datetime.now()
        else:
            logging.debug(f'\n\n\n[DEBUG] (user_session.py):  user is not logged in, cannot refresh activity\n\n\n')
            self.last_active = None
            





    def user_activity_timeout(self):
        logging.debug(f'\n\n\n[DEBUG] (user_session.py):  user_activity_timeout called for user={self.user}\n\n\n')
        if not self.logged_in or self.last_active is None:
            logging.debug(f'\n\n\n[DEBUG] (user_session.py):  user is not logged in or last_active is None, returning False\n\n\n')
            return False
        
        logging.debug(f'\n\n\n[DEBUG] (user_session.py):  user is logged in, checking timeout\n\n\n')
        return (datetime.now() - self.last_active) > timedelta(minutes = 5)




session = Session()