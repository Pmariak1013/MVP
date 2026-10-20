from utils.db import DB
from utils.user_session import session
from utils import menu_module, report
#from standard_user_menu.query_by_player.player_selected_state import STATE

import logging


def isValidName(name):

    if not name:
        return False
    for char in name:
        if (not char.isalpha() and char != ' '):
            return False
    return True





def getTeamNameInput():

    while True:

        print(f"\n{'=' * 60}")

        team_input = input("Enter team name or correct 3-letter abbreviation: ").strip()

        if not isValidName(team_input):
            print("\nInvalid first name. Please use only letters, spaces, or hyphens.\n")
            continue

        query = "SELECT full_name FROM nba_stats.team WHERE full_name ILIKE %s"
        
        params = (team_input + "%", )


        rows, headers = DB.query(query = query, connect_type = "standard_user", params = params)

        if len(rows) == 0:
            print("\nNo teams found with that name. Please try again.\n")
            continue

        elif len(rows) == 1:
            #report.print_report(rows, headers)
            print(f'Team selected: {rows[0][0]}')
            session.team_selected_name = rows[0][0]
            return True
        
        elif len(rows) > 1:
            print(f'Error fetching team. Please try again.\n')
            return False
        
        return False



def getTeamSeasonHistory(team_name):
    query = """
            SELECT T.full_name, TSS.season_id, TSS.wins, TSS.losses, CAST(TSS.wins AS DECIMAL(6,2)) / TSS.gp * 100 AS win_percentage, CAST(TSS.fgm AS DECIMAL(6,2)) / TSS.fga * 100 AS fg_percentage, CAST(TSS.fg3m AS DECIMAL(6,2)) / TSS.fg3a * 100 AS "3pt_percentage"
            FROM nba_stats.team AS T
            JOIN nba_stats.team_season_stats AS TSS ON T.team_id = TSS.team_id
            WHERE (T.full_name ILIKE %s OR T.abbreviation ILIKE %s) AND TSS.season_type = 'R'
            ORDER BY TSS.season_id ASC;
        """
    
    params = (f'%{team_name}%', f'%{team_name}%')

    results, headers = DB.query(query = query, params = params, connect_type = 'standard_user')

    if not results:
        print()
        print(f"No season history found for team: {team_name}")
        print()
    else:
        report.print_report(results, headers)
    DB.close()
    return results