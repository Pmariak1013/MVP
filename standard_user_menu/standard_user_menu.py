from utils.menu_module import menu_module
from standard_user_menu import standard_user_queries as Queries
from utils.user_session import session
import logging

from standard_user_menu.query_by_player import player_queries as PlayerQueries
from standard_user_menu.query_by_player import query_by_player_menu as PlayerMenu
from standard_user_menu.query_by_team import query_by_team_menu as TeamMenu
from standard_user_menu.query_by_team import team_queries as TeamQueries


#from standard_user_menu.query_by_player.player_selected_state import STATE



def standard_user_menu():
    logging.debug("\n\n\n[DEBUG] Call to standard_user_menu()")
    logging.debug(f'\n\n[DEBUG] (standar_user_menu) session.player_selected_state: {session.player_selected_state}\n\n')
    
    if session.player_selected_state:
        options = {
            1: (f"Lookup Stats for {session.player_selected_name}:", PlayerMenu.query_by_player_menu),
            2: ("Lookup Stats for a Different Player:", check_player_selected),
            3: ("Get Players who Scored the Most in One Game:", Queries.getMostPoints),
            #4: ("Get Team Season History:", processTeamInput),
            4: ("Get Players with Most Playoff Games:", Queries.getPlayersWithMostPlayoffGames),
            5: ("Get Most Recent NBA Games", Queries.getMostRecentGames),
            6: ("Get Results for a Specific Season", processSeasonInput)
        }
    else: 
        options = {
            1: ("Lookup Stats by Player Name:", check_player_selected),
            2: ("Lookup Stats by Team:", processTeamInput),
            3: ("Get Players who Scored the Most in One Game:", Queries.getMostPoints),
            #3: ("Get Team Season History:", processTeamInput),
            4: ("Get Players with Most Playoff Games:", Queries.getPlayersWithMostPlayoffGames),
            5: ("Get Most Recent NBA Games", Queries.getMostRecentGames),
            6: ("Get Results for a Specific Season", processSeasonInput)
        }
    menu_module(menu_title = "Standard User Menu", options_dict = options, prevMenu = "Main Menu", mainMenu = False)



def check_player_selected():

    logging.debug("\n\n\n[DEBUG] Call to check_player_selected()")

    player_result = PlayerQueries.getPlayerNameInput()

    if player_result:
        print('\n\nPlayer selected, going to player menu.\n\n')
        session.player_selected_state = True
        print(f'\n\n[DEBUG] session.player_selected_state: {session.player_selected_state}\n\n')
        print(f'\n\n[DEBUG] session.player_selected_name: {session.player_selected_name}\n\n')
        PlayerMenu.query_by_player_menu(player_selected_state = True)
    else:
        print('\n\nNo player selected, returning to standard user menu.\n\n')
        session.player_selected_state = False
        standard_user_menu()



def processTeamInput():
    result = TeamQueries.getTeamNameInput()

    if result:
        TeamMenu.query_by_team_menu()
    else:
        print("No team name or abbreviation entered. Returning to standard user menu.")
        standard_user_menu()



def processSeasonInput():
    result = Queries.getSeasonInput()

    if result:
        Queries.getResultsForSeason(result)
    else:
        print(f'Error fetching season, returning to standard user menu.\n')
        return