from utils import menu_module
from utils.user_session import session
from admin_menu.admin_menu_queries import *
from logins.logout import logout
from datetime import datetime
import logging



# admin menu
def admin_menu():
    logging.debug(f'[DEBUG] (admin_menu.py) session privilege level: {session.privilege}')

    # if the current session's user is logged in and has admin level privileges, display full admin options.
    if session.privilege == 1 and session.logged_in:
        options = {
            1: ("View All Users.", viewAllUsers),
            2: ("Delete A User.", delteUserWrapper),
            3: ("Update Database to October 21st, 2025 Data.", update_DB_to_oct_21_2025),
            4: ("Logout of Admin Account.", logout)
        }

    # if the current session's user is logged in, but does not have admin privileges, deny them the full admin options.
    elif session.logged_in and session.privilege != 1:
        options = {
            1 :("Logout of Standard Account Before Attempting Admin Login.", logout),
        }

    # if current session's user is not logged in at all, only give them option to login to admin account.
    else:
        options = {
            1 :("Attempt Admin Login.", attemptAdminLoginWrapper)
        }
    menu_module.menu_module(menu_title = "Admin Menu", options_dict = options, prevMenu = "Main Menu", mainMenu = False)



# helper function to handle the user attempt to login to admin account.
def attemptAdminLoginWrapper():
    # stores the result of getting user input.
    result = attemptAdminLogin()

    # if login attempt returned true, login to python-side session as admin.
    if result:
        logging.debug(f'[DEBUG] (admin_menu.py) admin login successful for user: admin')
        session.login(user = 'admin', priv = 1)
    
    # if login attempt failed, just ensure current session privilege stays = 0.
    else:
        logging.debug(f'[DEBUG] (admin_menu.py) admin login failed')
        session.privilege = 0


    logging.debug(f'[DEBUG] (admin_menu.py) session privilege level after login attempt: {session.privilege}')

    # return to the admin menu.
    admin_menu()


def delteUserWrapper():
    username = input("Enter the username of the user to delete: ")
    deleteUser(username)