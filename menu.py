from utils import menu_module
from standard_user_menu.standard_user_menu import standard_user_menu
from admin_menu.admin_menu import admin_menu
from logins.login_menu import login_menu
from utils.user_session import session
import logging
from pyfiglet import Figlet


# main menu
def menu():

    # title screen print outs
    print(f'\n\n\n{"=" * 60}\n{"=" * 60}\n{"=" * 60}\n')

    f = Figlet(width=60)  # default font
    print(f.renderText('NBA  Stats'))
    print(f.renderText('Database  App'))

    # options presented to user at program start (main menu)
    options = {
        1 :("NBA Stats for Guest Users.", standard_user_menu),
        2 :("Standard User Account Menu.", login_menu),
        3 :("Admin Account Menu.", admin_menu)
    }

    # calls the menu module function with menu = Main Menu
    menu_module.menu_module(menu_title = "Main Menu", options_dict = options, prevMenu = "Main Menu", mainMenu = True)

# used for debugging print outs
#logging.basicConfig(level=logging.DEBUG)
#logging.basicConfig(level=logging.INFO)

#if __name__ == "__main__":
#    menu()