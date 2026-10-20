from utils.user_session import session
from utils.login_utils import refresh_activity, user_activity_timeout
import logging
from utils.login_utils import logoutAllUsers
from pyfiglet import Figlet







def menu_module(menu_title, options_dict, prevMenu = None, mainMenu=False, submenu=False):
    """
        options_dict: dictionary --> i: (text, function)
        Example:
        options_dict = {
            1: ("View Teams", view_teams_function),
            2: ("Add Team", add_team_function),
            n: ("Text", function),
            
            Exit code will be esc key on keyboard as option n+1
    """


    '''
    if not submenu:

        status = 0
        if session.logged_in:
            if session.user:
                status = 1                                



        print(f'\n{"=" * 55}\n                                   [ {"Logged in: " + session.user if status == 1 and session.user else "Not logged in."} ]\n')
        print(f"\nWelcome to the {menu_title}\n")
        #f = Figlet(width=60, font = 'small')  # default font
        #print(f.renderText(f'\n{menu_title}\n'))
        print(f'{"=" * 55}\n')


    else:
        print(f'\n{"=" * 55}\n                                   [ Not logged in. ]\n')
        print(f"\nWelcome to the {menu_title}\n")
        #f = Figlet(width=60, font = 'small')  # default font
        #print(f.renderText(f'\n{menu_title}\n'))
        print(f'{"=" * 55}\n')

    '''

    
    # keep looping until user goes back to previous or program exits
    running = True
    while running:

        
        # at every loop of menu being displayed, first check for session timeout
        #print(f'\n[DEBUG]: menu_module loop began again. checking if user is loggeed and if so then for session timeout:\n')
        if session.logged_in:
            old_name = session.user
            if user_activity_timeout(old_name):
                print(f"Session expired. {old_name} has been logged out for inactivity.")
                continue
            
            # reset user last active timestamp
            refresh_activity(session.user)

        # forces user to provide a valid input, menu cannot just be exited by random inputs.
        good_input = False
        while not good_input:

            #print(f'\n[DEBUG]: inside menu_module good_input loop, next line calls options_dict function.\n')

            # get the refreshed options for the current menu...
            # we want the options to be dynamic based on login state, standard_user vs admin, player selected or not, etc.
            if callable(options_dict):
                options_dict = options_dict()
            else:
                options_dict = options_dict
            #options_dict = options_dict() if callable(options_dict) else options_dict

            
            # if logged in, ALWAYS show username
            # if not logged in, ALWAYS show not logged in

            # if player selected, ONLY show when in Player Stats Menu
            # if in Player Stats Menu, ALWAYS show the player selected or that there is none.



            if not session.logged_in:
                if session.player_selected_state and menu_title == 'Player Stats Menu':
                    print(f'\n{"=" * 55}\n                                   [ Not logged in. ]')
                    print(f"{menu_title}    - Player Selected: {session.player_selected_name[0]} {session.player_selected_name[1]}")
                    print(f'\n{"=" * 55}\n')
                else:
                    print(f'\n{"=" * 55}\n                                   [ Not logged in. ]')
                    print(f"{menu_title}")
                    print(f'\n{"=" * 55}\n')
            else:
                if session.player_selected_state and menu_title == 'Player Stats Menu':
                    print(f'\n{"=" * 55}\n                                   [ Logged in: {session.user} ]')
                    print(f"{menu_title}    - Player Selected: {session.player_selected_name[0]} {session.player_selected_name[1]}")
                    print(f'\n{"=" * 55}\n')
                else:
                    print(f'\n{"=" * 55}\n                                   [ Logged in: {session.user} ]')
                    print(f"{menu_title}")
                    print(f'\n{"=" * 55}\n')




            # display options to user in the terminal
            for i, (text, _) in options_dict.items():
               
                print(f"{i}. {text}\n")

            if menu_title == "Main Menu":
                print(f"{len(options_dict)+1}. Quit App. \n")
            else:
                print(f"{len(options_dict)+1}. Exit {menu_title}, return to {prevMenu}.\n")

            # gets user inputted choice
            try:
                user_input = int((input("Please select an option: ").strip()))
                good_input = True

            # handles invalid inputs (not the displayed integers)
            except ValueError:
                print("\nPlease pick a valid option and try again.\n\n\n")
                continue
        

        # processes result of user choice by calling the corresponding function
        if user_input not in [i for i in range(1, len(options_dict)+1)]:

            # Exit code will be last index in dict (corresponds to the last option displayed)
            if user_input == len(options_dict)+1:
                if menu_title == "Main Menu":
                    print(f"Exiting {menu_title} menu. Goodbye!\n\n")
                    logoutAllUsers()
                    return
                else:
                    print(f"Exiting {menu_title} menu. Returning to {prevMenu}\n\n")
                return

            else:
                print("Invalid option selected. Please try again.\n\n\n")
                continue
            

        # extract function associated with user inputted choice
        function = options_dict[user_input][1]
        print("")  # For better formatting


        # debugging printout
        logging.debug(f'\n\n\n[DEBUG]: now calling refresh_activity for user: {session.user}\n\n\n')

        # checks for user timeout, resets user last active timestamp
        refresh_activity(session.user)

        # executes the selected function.
        function()

        if menu_title == "Login Menu":
            return
        
        
        
        if not mainMenu:
            print(f"\nWould you like to use {menu_title} again? (Y/N) (N -> go back to {prevMenu})")
            valid_input = False
            while not valid_input:
                choice = input("Enter your choice: ").strip().upper()
                if choice == 'Y':
                    valid_input = True
                elif choice == 'N':
                    print(f"Returning to {menu_title}).\n\n")
                    return
                else:
                    print("Invalid input. Please enter Y or N.\n")

        