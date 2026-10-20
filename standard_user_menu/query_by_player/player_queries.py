from utils.db import DB
from utils.user_session import session
from utils import menu_module, report
#from standard_user_menu.query_by_player.player_selected_state import STATE

import logging


def isValidName(name):

    accents = 'áàäâãåçéèëêíìïîñóòöôõúùüûýÿÁÀÄÂÃÅÇÉÈËÊÍÌÏÎÑÓÒÖÔÕÚÙÜÛÝ'

    if not name:
        return False
    for char in name:
        if (not char.isalpha() and char != ' 'and char != '-' and char not in accents):
            return False
    return True





def getPlayerNameInput():

    while True:

        print(f"\n{'=' * 60}")

        fname_input = input("Enter player first name: ").strip()

        if not isValidName(fname_input):
            print("\nInvalid first name. Please use only letters, spaces, or hyphens.\n")
            continue

        lname_input = input("Enter player last name: ").strip()

        if not isValidName(lname_input):
            print("\nInvalid last name. Please use only letters, spaces, or hyphens.\n")
            continue

        query = "SELECT fname, lname, dob FROM nba_stats.player WHERE unaccent(fname) ILIKE %s AND unaccent(lname) ILIKE %s"
        
        params = (fname_input + "%", lname_input + "%")


        rows, headers = DB.query(query = query, connect_type = "standard_user", params = params)

        if len(rows) == 0:
            print("\nNo players found with that name. Please try again.\n")
            continue

        elif len(rows) == 1:
            #report.print_report(rows, headers)
            session.player_selected_state = True
            session.player_selected_name = (rows[0][0], rows[0][1])
            logging.debug(f"\n[DEBUG] from getPlayerNameInput:   Player '{rows[0][0]} {rows[0][1]}' selected.\n")
            return True
        
        elif len(rows) > 1:
            print("\nMultiple players found with that name. Please select one from the list below:\n")
            for i, row in enumerate(rows):
                print(f"{i + 1}. {row['fname']} {row['lname']} (DOB: {row['dob']})")
            
            while True:
                try:
                    choice = int(input("\nEnter the number of the player you want to select: "))
                    if 1 <= choice <= len(rows):
                        return rows[choice - 1]
                    else:
                        print("Invalid choice. Please try again.")
                except ValueError:
                    print("Invalid input. Please enter a number.")



def getPlayerCareerBaseStats(player_name):

    logging.debug(f"[DEBUG] from getPlayerCareerBaseStats:   player_name = {player_name}")

    query = """
    SELECT P.fname, P.lname, PCS.season_id, PCS.season_type, T.full_name, CAST(PCS.pts / PCS.gp AS DECIMAL(4,2)) AS ppg, PCS.gp, PCS.pts, PCS.ast, PCS.reb, PCS.steals, PCS.blk
    FROM nba_stats.player_career_stats AS PCS
    JOIN nba_stats.player AS P ON P.player_id = PCS.player_id
    JOIN nba_stats.team AS T ON T.team_id = PCS.team_id
    WHERE unaccent(P.fname) ILIKE unaccent(%s) AND unaccent(P.lname) ILIKE unaccent(%s)
    ORDER BY season_id ASC, season_type DESC;
    """

    params = (player_name[0], player_name[1])

    rows, headers = DB.query(query = query, connect_type = "standard_user", params = params)


    '''
    season_type_map = {
        'R': 'Regular Season',
        'P': 'Playoffs'
        }
    
    for row in rows:
        row['season_type'] = season_type_map.get(row['season_type'], '')

        
    '''

    if len(rows) == 0:
        print("\nNo career stats found for that player.\n")
        return False
    else:
        report.print_report(rows, headers)
        return True


def getPlayerCareerAdvancedStats(player_name):

    logging.debug(f"[DEBUG] from getPlayerCareerAdvancedStats:   player_name = {player_name}")

    query = """
    SELECT P.fname AS First_Name, P.lname AS Last_Name, PCAS.season_id AS Season, PCAS.season_type AS Season_Type, T.full_name AS Team, PCAS.def_rating, PCAS.off_rating, PCAS.efg_pct, PCAS.ts_pct, PCAS.usg_pct, PCAS.pace, PCAS.poss
    FROM nba_stats.player_career_advanced_stats AS PCAS
    JOIN nba_stats.player AS P ON P.player_id = PCAS.player_id
    JOIN nba_stats.team AS T ON T.team_id = PCAS.team_id
    WHERE unaccent(P.fname) ILIKE unaccent(%s) AND unaccent(P.lname) ILIKE unaccent(%s)
    ORDER BY season_id ASC;
    """

    params = (player_name[0], player_name[1])

    rows, headers = DB.query(query = query, connect_type = "standard_user", params = params)


    '''
    season_type_map = {
        'R': 'Regular Season',
        'P': 'Playoffs'
        }
    
    for row in rows:
        row['season_type'] = season_type_map.get(row['season_type'], '')

        
    '''

    if len(rows) == 0:
        print("\nNo career stats found for that player.\n")
        return False
    else:
        report.print_report(rows, headers)
        return True


def getPlayerPlayoffCareerStats(player_name):

    logging.debug(f"[DEBUG] from getPlayerPlayoffStats:   player_name = {player_name}")

    query = """
    SELECT P.fname, P.lname, PCS.season_id, T.full_name, CAST(PCS.pts / PCS.gp AS DECIMAL(4,2)) AS ppg, PCS.gp, PCS.pts, PCS.ast, PCS.reb, PCS.steals, PCS.blk
    FROM nba_stats.player_career_stats AS PCS
    JOIN nba_stats.player AS P ON P.player_id = PCS.player_id
    JOIN nba_stats.team AS T ON T.team_id = PCS.team_id
    WHERE unaccent(P.fname) ILIKE unaccent(%s) AND unaccent(P.lname) ILIKE unaccent(%s) AND PCS.season_type = 'P'
    ORDER BY season_id ASC;
    """

    params = (player_name[0], player_name[1])

    rows, headers = DB.query(query = query, connect_type = "standard_user", params = params)

    if len(rows) == 0:
        print("\nNo playoff stats found for that player.\n")
        return False
    else:
        report.print_report(rows, headers)
        return True
    


def getPlayerCareerAdvStatsAndBestGame(player_name):
    #return None


    # first subquery gets the max points the target player scored in a game for each (season_id, season_type) pair 
    # present in player_career_advanced_stats


    # second subquery gets the date of that game by getting all performances for the target player for each (season_id, season_type) pair, 
    # ordering by points desc and date asc (if tie chooses earliest), and limiting to 1 result

    query = """
            SELECT P.fname, P.lname, PCAS.season_id, PCAS.season_type, T.full_name,
            (
                SELECT MAX(PP.pts)
                FROM nba_stats.player_performance AS PP
                JOIN nba_stats.player AS P2 
                    ON P2.player_id = PP.player_id
                JOIN nba_stats.game_info AS GI
                    ON GI.game_id = PP.game_id
                WHERE unaccent(P2.fname) ILIKE unaccent(%s) AND unaccent(P2.lname) ILIKE unaccent(%s)
                    AND GI.season_id = PCAS.season_id AND GI.game_type = PCAS.season_type
            ) AS max_points,

            (
                SELECT GI2.date_played
                FROM nba_stats.game_info AS GI2
                JOIN nba_stats.player_performance AS PP2
                    ON GI2.game_id = PP2.game_id
                JOIN nba_stats.player AS P3
                    ON P3.player_id = PP2.player_id
                WHERE unaccent(P3.fname) ILIKE unaccent(%s) AND unaccent(P3.lname) ILIKE unaccent(%s)
                    AND GI2.season_id = PCAS.season_id AND GI2.game_type = PCAS.season_type
                ORDER BY PP2.pts DESC, GI2.date_played ASC
                LIMIT 1
            ) AS date,

            PCAS.usg_pct, PCAS.efg_pct, PCAS.ts_pct

            FROM nba_stats.player_career_advanced_stats AS PCAS
            JOIN nba_stats.player AS P 
                ON P.player_id = PCAS.player_id
            JOIN nba_stats.team AS T
                ON T.team_id = PCAS.team_id
            WHERE unaccent(P.fname) ILIKE unaccent(%s) AND unaccent(P.lname) ILIKE unaccent(%s)
            ORDER BY PCAS.season_id ASC, PCAS.season_type DESC;
            
            """
    
    params = (player_name[0], player_name[1], player_name[0], player_name[1], player_name[0], player_name[1])

    rows, headers = DB.query(query = query, connect_type = "standard_user", params = params)

    if len(rows) == 0:
        print("\nNo advanced stats or best game data found for that player.\n")
        return False
    else:
        report.print_report(rows, headers)
        return True
    


def getBestSeasons(player_name):
    query = """
            SELECT P.fname, P.lname, PCS.season_id, PCS.season_type, T.full_name AS team, (PCS.pts / PCS.gp) AS ppg, PCAS.ts_pct, MAX(PP.pts) AS most_pts
            FROM nba_stats.player AS P
            JOIN nba_stats.player_career_stats AS PCS
                ON P.player_id = PCS.player_id
            JOIN nba_stats.player_career_advanced_stats AS PCAS
                ON PCS.player_id = PCAS.player_id AND PCAS.season_id = PCS.season_id AND PCAS.season_type = PCS.season_type AND PCAS.team_id = PCS.team_id
            JOIN nba_stats.team AS T
                ON T.team_id = PCS.team_id AND T.team_id = PCAS.team_id
            JOIN nba_stats.player_performance AS PP
                ON P.player_id = PP.player_id
            JOIN nba_stats.game_info AS GI
                ON PP.game_id = GI.game_id AND GI.season_id = PCS.season_id AND GI.game_type = PCS.season_type
            WHERE unaccent(P.fname) ILIKE unaccent(%s) AND unaccent(P.lname) ILIKE unaccent(%s)
            GROUP BY (P.fname, P.lname, T.full_name, PCS.season_id, PCS.season_type, PCS.team_id, PCS.pts, PCS.gp, PCAS.ts_pct)
            ORDER BY PCS.season_id DESC, PCS.season_type ASC;
            """
    
    params = (player_name[0], player_name[1])

    rows, headers = DB.query(query = query, connect_type = "standard_user", params = params)

    if len(rows) == 0:
        print("\nNo data found for that player.\n")
        return False
    else:
        report.print_report(rows, headers)
        return True