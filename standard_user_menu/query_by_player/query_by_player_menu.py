from utils.menu_module import menu_module
from standard_user_menu import standard_user_queries as Queries
from standard_user_menu.query_by_player import player_queries
from utils.user_session import session
import logging

from standard_user_menu.query_by_player.player_queries import getPlayerNameInput

#from standard_user_menu.query_by_player.player_selected_state import STATE

#player_selected = STATE


#print(f'\n\n[DEBUG] before query_by_player_menu(), player_selected state is: {session.player_selected_state}\n\n')


def query_by_player_menu(player_selected_state = False):
    #logging.debug("\n\n\n[DEBUG] player_selected_state: " + str(player_selected))
    
    
    #print(f'\n\n[DEBUG] In query_by_player_menu(), player_selected state is: {session.player_selected_state}\n\n')
    #print(f'\n\n[DEBUG] In query_by_player_menu(), player_name  is: {session.player_selected_name}\n\n')

    if session.player_selected_state and session.player_selected_name != (None, None):
        player_name = f'{session.player_selected_name[0]} {session.player_selected_name[1]}'
        options = {
            1: (f"Get {player_name}'s Career Base Stats:", lambda: player_queries.getPlayerCareerBaseStats(session.player_selected_name)),
            2: (f"Get {player_name}'s Career Advanced Stats:", lambda: player_queries.getPlayerCareerAdvancedStats(session.player_selected_name)),
            3: (f"Get {player_name}'s Playoff Career Stats", lambda: player_queries.getPlayerPlayoffCareerStats(session.player_selected_name)),
            4: (f"Get {player_name}'s Highest Scoring Game Per Season:", lambda: player_queries.getPlayerCareerAdvStatsAndBestGame(session.player_selected_name)),
            5: (f"Get {player_name}'s Best Seasons:", lambda: player_queries.getBestSeasons(session.player_selected_name)),
            6: ("Lookup Another Player's Stats:", reset_player_selection)
            
        }
    else:
        options = {
            1: ("Lookup Player Stats by Name:", getPlayerNameInput),
            2: ("Get Highest Scoring Player Performances:", Queries.getMostPoints)
        }
    menu_module(menu_title = "Player Stats Menu", options_dict = options, prevMenu = "Standard User Menu", mainMenu = False)


def reset_player_selection():
    result = getPlayerNameInput()

    query_by_player_menu()