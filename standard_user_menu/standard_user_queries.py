from utils.db import DB
from utils.user_session import session
from utils import menu_module, report
import logging

       
def getMostPoints():
    logging.debug(f'getMostPoints() called from standard_user_queries.py')
    #DB.connect_standard_user()
    print(f"Highest scoring performances:")
    results, headers = DB.query(query = "SELECT P.fname, P.lname, PP.pts, GI.date_played " \
                                        "FROM nba_stats.player AS P JOIN nba_stats.player_performance AS PP ON P.player_id = PP.player_id " \
                                        "JOIN nba_stats.game_info AS GI ON GI.game_id = PP.game_id " \
                                        "ORDER BY PP.pts DESC LIMIT 20;", connect_type = 'standard_user')
    if not results:
        print()
        print(f"No results found!")
        print()
    
    else:
        report.print_report(results,headers)
    DB.close()
    return results


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



def getPlayersWithMostPlayoffGames():


    query = """ 
            SELECT P.fname AS first_name, P.lname AS last_name, SUM(PCS.gp) AS total_playoff_games
            FROM nba_stats.player AS P
            JOIN nba_stats.player_career_stats AS PCS ON P.player_id = PCS.player_id
            WHERE PCS.season_type = 'P'
            GROUP BY P.player_id
            ORDER BY total_playoff_games DESC
            LIMIT 10;

        """
    
    results, headers = DB.query(query = query, connect_type = 'standard_user')

    if not results:
        print()
        print("No players found with playoff games.")
        print()
    else:
        report.print_report(results, headers)
    DB.close()
    return


def getMostRecentGames():
    query = """SELECT DISTINCT GI.date_played, T1.full_name,  TGS1.pts, T2.full_name, TGS2.pts
                FROM nba_stats.game_info AS GI
                JOIN nba_stats.game_team_stats AS TGS1
                    ON GI.game_id = TGS1.game_id AND GI.home_team = TGS1.team_id
                JOIN nba_stats.game_team_stats AS TGS2
                    ON TGS1.game_id = TGS2.game_id AND GI.away_team = TGS2.team_id
                JOIN nba_stats.team AS T1
                    ON T1.team_id = GI.home_team
                JOIN nba_stats.team AS T2
                    ON T2.team_id = GI.away_team
                ORDER BY GI.date_played DESC
                LIMIT 10;    
    """

    results, headers = DB.query(query = query, connect_type = 'standard_user')

    if not results:
        print()
        print("No players found with playoff games.")
        print()
    else:
        report.print_report(results, headers)
    DB.close()
    return


def getResultsForSeason(season):
    query = """SELECT DISTINCT GI.date_played, T1.full_name, TGS1.pts, T2.full_name, TGS2.pts
                FROM nba_stats.game_info AS GI
                JOIN nba_stats.game_team_stats AS TGS1
                    ON GI.game_id = TGS1.game_id AND GI.home_team = TGS1.team_id
                JOIN nba_stats.game_team_stats AS TGS2
                    ON TGS1.game_id = TGS2.game_id AND GI.away_team = TGS2.team_id
                JOIN nba_stats.team AS T1
                    ON T1.team_id = GI.home_team
                JOIN nba_stats.team AS T2
                    ON T2.team_id = GI.away_team
                WHERE GI.season_id = %s
                ORDER BY GI.date_played ASC;
    """

    results, headers = DB.query(query = query, connect_type = 'standard_user', params = (season, ))

    if not results:
        print()
        print("No players found with playoff games.")
        print()
    else:
        report.print_report(results, headers)
    DB.close()
    return


def getSeasonInput():
    seasons = ['2000-01', '2001-02', '2002-03', '2003-04', '2004-05', '2005-06', '2006-07', '2007-08', '2008-09', '2009-10',
               '2010-11', '2011-12', '2012-13', '2013-14', '2014-15', '2015-16', '2016-17', '2017-18', '2018-19', '2019-20',
               '2020-21', '2021-22', '2022-23', '2023-24', '2024-25']
    
    invalid_input = True
    while invalid_input:
        print(f'(Supports seasons from 2000-01 to 2024-25, enter in that format.)\n')
        season = input("Please enter desired season:").strip()
        if season in seasons:
            invalid_input = False

    return season


'''
def getChampions():
    query = """
            SELECT GI.season_id, T.full_name, MAX(GI.date_played) AS game_date
            FROM nba_stats.game_info AS GI
            JOIN nba_stats.game_team_stats AS GTS
                ON GI.game_id = GTS.game_id
            JOIN nba_stats.team AS T
                ON GTS.team_id = T.team_id
            WHERE GI.season_id <= '2024-25'
            GROUP BY GI.season


        """

'''