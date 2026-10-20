from utils.menu_module import menu_module
from standard_user_menu import standard_user_queries as Queries
from utils.user_session import session
from standard_user_menu.query_by_team import team_queries
from standard_user_menu.query_by_team.team_queries import getTeamNameInput

import logging


def query_by_team_menu(player_selected_state = False):

  
    if session.team_selected_name != None:
        team_name = f'{session.team_selected_name}'
        options = {
            1 : (f"Get Seasons History for {team_name}", lambda: team_queries.getTeamSeasonHistory(team_name)),
            2 : (f"Select a different team:", getTeamNameInput)
            
        }
    else:
        options = {
            1 : (f"Select a team to get stats for:", getTeamNameInput)

        }
    menu_module(menu_title = "Team Stats Menu", options_dict = options, prevMenu = "Standard User Menu", mainMenu = False)


def reset_team_selection():
    result = getTeamNameInput()

    query_by_team_menu()