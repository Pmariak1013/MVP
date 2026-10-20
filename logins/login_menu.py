from utils.menu_module import menu_module
from utils.user_session import session
from .login import login
from .logout import logout
from .register import signup
from .forgot_password import forgot_password 
from .delete_account import delete_account



def refresh_login_menu_options():
    print(f'\n[DEBUG]: call to refresh_login_menu_options()\n')
    #options = {
    #    1: (f"Log{'out' if session.logged_in else 'in'}.", logout if session.logged_in else login),
    #    2: ("Signup.", signup),
    #    #3: ("Delete your account.", delete_account),
    #    #3: ("Forgot password?", forgot_password)
    #}

    #if session.user == 'admin' and session.logged_in and session.privilege == 1:
    #    options = {
    #        1: ("Logout of admin account.", logout)
    #    }
    #    return options


    if session.logged_in:
        options = {
            1: ("Logout.", logout),
            2: ("Delete Your Standard Account. This cannot be undone.", delete_account)
        }
    else:
        options = {
            1: ("Standard User Login.", login),
            2: ("Register New Standard Account.", signup),
        }

    
    return options


def login_menu():
   menu_module(menu_title = "Login Menu", options_dict = refresh_login_menu_options, prevMenu = "Main Menu")


   '''
    options = {
        1: (f"Log{'out' if session.logged_in else 'in'}.", logout if session.logged_in else login),
        2: ("Signup.", signup),
        #3: ("Delete your account.", delete_account),
        #3: ("Forgot password?", forgot_password)
    }

    if session.user == 'admin' and session.logged_in and session.privilege == 1:
        options = {
            1: ("Logout of admin account.", logout)
        }

    '''
    
    #options = {
    #    1: ("Logout.", logout),
    #    #2: ("Forgot password?", forgot_password),
    #    2: ("Delete your account.", delete_account)
    #}

    