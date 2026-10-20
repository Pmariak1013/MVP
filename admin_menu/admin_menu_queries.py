from getpass import getpass
import logging 
from utils.db import DB
from utils.user_session import session
import psycopg2
from dotenv import load_dotenv
import os
from utils import report


# processes user attempting to login to an admin account.
def attemptAdminLogin():
    print("# ------ ADMIN LOGIN ------ #")

    # no while loop because admin login gets one attempt, admin should know their info more consistently.
    username = input("Username: ").strip()
    pw = getpass("Password: ").strip()

    

    # checks .env file for a match between input username and password with the DB admin user info
    if username == os.getenv("DB_ADMIN_USER") and pw == os.getenv("DB_ADMIN_USER_PASSWORD"):
        # informs user the login succeeded.
        print("\nAdmin login successful!\n\n\n")
        return True
    else:
        # informs user the login failed.
        print("\nAdmin login failed. Invalid credentials.\n\n\n")
        return False
    
    return


# admin privilege level function that lets them view all users in the User table.
def viewAllUsers():
    print("# ------ VIEW ALL USERS ------ #")

    # an extra check to make sure non-admin level privilege users don't see other users.
    # should never be reached as but just in case.
    if session.privilege != 1:
        print("Access denied. Admin privileges required to view all users.")
        return
    
    # no need for admin to see hashed password + salt, so just select everything else in User table.
    query = "SELECT username, privilege_level, is_active, last_active FROM nba_stats.user ORDER BY last_active DESC;"

    # store the query result.
    results, headers = DB.query(query = query, connect_type = 'admin')

    # if results is None, means query returns 0 records.
    if not results:
        print()
        print(f"No users found in the database.")
        print()
    else:
        report.print_report(results, headers)

    # ensure DB connection is closed.
    DB.close()
    return


# admin privilege level function that can delete a user from the User table if correct username is given.
def deleteUser(username):
    print("# ------ DELETE USER ------ #")

    # a backup check to ensure non-admin privilege level users can't delete any users.
    if session.privilege != 1:
        print("Access denied. Admin privileges required to delete a user.")
        return
    
    # first check if user with username exists
    query = "SELECT username FROM nba_stats.user WHERE username = %s;"
    params = (username, )

    results, headers = DB.query(query = query, params = params, connect_type = 'admin')

    # if results is None, means no user with given username exists in the User table.
    if not results:
        print()
        print(f"User '{username}' does not exist in the database.")
        print()
        # exit the function.
        return
    
    # a user was found, proceed.
    # now delete the user with found username.

    query = "DELETE FROM nba_stats.user WHERE username = %s;"
    params = (username, )

    DB.query(query = query, params = params, connect_type = 'admin')

    # ensure DB connection is closed.
    DB.close()

    return


# transaction based query that updates the entire database to be matching NBA data from the first day of the 2025-26 season.
# idea is to perform database date based updates to match NBA data with transactions so correctness is more guaranteed.
def update_DB_to_oct_21_2025():

    query = """

    START TRANSACTION;
        -- motivation for transaction: since the database is time-based for its updates, we cannot just randomly insert new data from more recent games.
        -- we need to use ACID principles to ensure our data gets correctly added either all at once or not at all. this makes it much easier to determine
        -- the exact state of the database in the context of dates/time compared to the data source (NBA games). 
        -- transactions allow us to ensure each update is complete or rolled back to try again. this gives us a reliable date of which
        -- the database correctly matches NBA records.

        -- this transactions inserts the first day of data from the new 2025-26 NBA season, which only had 2 games.
        -- this is consistent since the database before the transactions consists of data from 2000-01 season to 2024-25 season.
        -- it is important to note, that we did not have to first insert to the Player or Team table because there were no new teams
        -- or new players added on this day. But future updates should be able to process new players and potentially new teams.

        -- must insert any new players or teams first so no FK violations.
        -- but there are no new players or teams in this data, so we dont have to.

        -- insert new games first.
        INSERT INTO nba_stats.game_info(game_id, home_team, away_team, date_played, season_id, game_type) VALUES(22500001,1610612760,1610612745,'2025-10-21','2025-26','R') ON CONFLICT(game_id) DO NOTHING;
        INSERT INTO nba_stats.game_info(game_id, home_team, away_team, date_played, season_id, game_type) VALUES(22500002,1610612747,1610612744,'2025-10-21','2025-26','R') ON CONFLICT(game_id) DO NOTHING;

        -- insert the team stats for those new games.
        INSERT INTO nba_stats.game_team_stats(game_id, team_id, wl, fgm, fga, fg3m, fg3a, ftm, fta, oreb, dreb, reb, ast, blk, steals, tov, pf, pts, plus_minus) VALUES(22500001,1610612745,'L',43,97,11,39,27,31,16,36,52,23,5,6,22,26,124,-1) ON CONFLICT(game_id, team_id) DO NOTHING;
        INSERT INTO nba_stats.game_team_stats(game_id, team_id, wl, fgm, fga, fg3m, fg3a, ftm, fta, oreb, dreb, reb, ast, blk, steals, tov, pf, pts, plus_minus) VALUES(22500002,1610612744,'W',38,78,17,40,26,29,9,31,40,29,4,10,18,27,119,10) ON CONFLICT(game_id, team_id) DO NOTHING;
        INSERT INTO nba_stats.game_team_stats(game_id, team_id, wl, fgm, fga, fg3m, fg3a, ftm, fta, oreb, dreb, reb, ast, blk, steals, tov, pf, pts, plus_minus) VALUES(22500001,1610612760,'W',46,104,13,52,20,25,11,27,38,29,4,12,11,27,125,1) ON CONFLICT(game_id, team_id) DO NOTHING;
        INSERT INTO nba_stats.game_team_stats(game_id, team_id, wl, fgm, fga, fg3m, fg3a, ftm, fta, oreb, dreb, reb, ast, blk, steals, tov, pf, pts, plus_minus) VALUES(22500002,1610612747,'L',42,77,8,32,17,28,7,32,39,23,2,7,19,21,109,-10) ON CONFLICT(game_id, team_id) DO NOTHING;

        -- insert the player performance stats from those new games.
        INSERT INTO nba_stats.player_performance(player_id, game_id, minutes, fgm, fga, fg3m, fg3a, ftm, fta, oreb, dreb, reb, ast, blk, steals, tov, pf, pts, plus_minus, team_id) VALUES(1631095,22500001,41,7,15,2,6,0,0,3,2,5,0,0,1,0,4,16,2,1610612745) ON CONFLICT(player_id, game_id) DO NOTHING;
        INSERT INTO nba_stats.player_performance(player_id, game_id, minutes, fgm, fga, fg3m, fg3a, ftm, fta, oreb, dreb, reb, ast, blk, steals, tov, pf, pts, plus_minus, team_id) VALUES(1630578,22500001,48,12,24,5,8,10,11,4,7,11,7,1,2,4,5,39,9,1610612745) ON CONFLICT(player_id, game_id) DO NOTHING;
        INSERT INTO nba_stats.player_performance(player_id, game_id, minutes, fgm, fga, fg3m, fg3a, ftm, fta, oreb, dreb, reb, ast, blk, steals, tov, pf, pts, plus_minus, team_id) VALUES(203500,22500001,36,1,4,0,0,2,2,5,8,13,3,0,0,3,4,4,2,1610612745) ON CONFLICT(player_id, game_id) DO NOTHING;
        INSERT INTO nba_stats.player_performance(player_id, game_id, minutes, fgm, fga, fg3m, fg3a, ftm, fta, oreb, dreb, reb, ast, blk, steals, tov, pf, pts, plus_minus, team_id) VALUES(201142,22500001,47,9,16,0,4,5,6,0,9,9,3,0,0,4,6,23,0,1610612745) ON CONFLICT(player_id, game_id) DO NOTHING;
        INSERT INTO nba_stats.player_performance(player_id, game_id, minutes, fgm, fga, fg3m, fg3a, ftm, fta, oreb, dreb, reb, ast, blk, steals, tov, pf, pts, plus_minus, team_id) VALUES(1641708,22500001,38,8,17,0,7,2,2,2,2,4,5,1,1,4,3,18,-11,1610612745) ON CONFLICT(player_id, game_id) DO NOTHING;
        INSERT INTO nba_stats.player_performance(player_id, game_id, minutes, fgm, fga, fg3m, fg3a, ftm, fta, oreb, dreb, reb, ast, blk, steals, tov, pf, pts, plus_minus, team_id) VALUES(1631106,22500001,21,1,6,1,4,0,0,0,6,6,0,1,0,4,1,3,-4,1610612745) ON CONFLICT(player_id, game_id) DO NOTHING;
        INSERT INTO nba_stats.player_performance(player_id, game_id, minutes, fgm, fga, fg3m, fg3a, ftm, fta, oreb, dreb, reb, ast, blk, steals, tov, pf, pts, plus_minus, team_id) VALUES(1642263,22500001,27,3,11,2,7,1,2,1,1,2,4,1,1,2,1,9,0,1610612745) ON CONFLICT(player_id, game_id) DO NOTHING;
        INSERT INTO nba_stats.player_performance(player_id, game_id, minutes, fgm, fga, fg3m, fg3a, ftm, fta, oreb, dreb, reb, ast, blk, steals, tov, pf, pts, plus_minus, team_id) VALUES(203991,22500001,7,1,1,0,0,2,2,0,0,0,0,0,1,1,0,4,5,1610612745) ON CONFLICT(player_id, game_id) DO NOTHING;
        INSERT INTO nba_stats.player_performance(player_id, game_id, minutes, fgm, fga, fg3m, fg3a, ftm, fta, oreb, dreb, reb, ast, blk, steals, tov, pf, pts, plus_minus, team_id) VALUES(1629006,22500001,19,1,3,1,3,5,6,1,1,2,1,1,0,0,2,8,-8,1610612745) ON CONFLICT(player_id, game_id) DO NOTHING;


        INSERT INTO nba_stats.player_performance(player_id, game_id, minutes, fgm, fga, fg3m, fg3a, ftm, fta, oreb, dreb, reb, ast, blk, steals, tov, pf, pts, plus_minus, team_id) VALUES(1628983,22500001,47,12,26,1,9,10,14,0,5,5,5,2,2,3,2,35,3,1610612760) ON CONFLICT(player_id, game_id) DO NOTHING;
        INSERT INTO nba_stats.player_performance(player_id, game_id, minutes, fgm, fga, fg3m, fg3a, ftm, fta, oreb, dreb, reb, ast, blk, steals, tov, pf, pts, plus_minus, team_id) VALUES(1631096,22500001,38,11,17,2,5,4,4,2,5,7,2,0,0,3,6,28,-1,1610612760) ON CONFLICT(player_id, game_id) DO NOTHING;
        INSERT INTO nba_stats.player_performance(player_id, game_id, minutes, fgm, fga, fg3m, fg3a, ftm, fta, oreb, dreb, reb, ast, blk, steals, tov, pf, pts, plus_minus, team_id) VALUES(1641717,22500001,41,5,10,3,8,1,2,1,6,7,5,0,4,2,3,14,8,1610612760) ON CONFLICT(player_id, game_id) DO NOTHING;
        INSERT INTO nba_stats.player_performance(player_id, game_id, minutes, fgm, fga, fg3m, fg3a, ftm, fta, oreb, dreb, reb, ast, blk, steals, tov, pf, pts, plus_minus, team_id) VALUES(1628392,22500001,36,2,5,0,1,2,2,5,3,8,5,0,2,1,6,6,9,1610612760) ON CONFLICT(player_id, game_id) DO NOTHING;
        INSERT INTO nba_stats.player_performance(player_id, game_id, minutes, fgm, fga, fg3m, fg3a, ftm, fta, oreb, dreb, reb, ast, blk, steals, tov, pf, pts, plus_minus, team_id) VALUES(1629652,22500001,45,2,12,0,8,2,2,2,4,6,5,0,1,1,4,6,2,1610612760) ON CONFLICT(player_id, game_id) DO NOTHING;
        INSERT INTO nba_stats.player_performance(player_id, game_id, minutes, fgm, fga, fg3m, fg3a, ftm, fta, oreb, dreb, reb, ast, blk, steals, tov, pf, pts, plus_minus, team_id) VALUES(1642349,22500001,14,6,12,3,6,1,1,1,1,2,2,1,0,0,2,16,2,1610612760) ON CONFLICT(player_id, game_id) DO NOTHING;
        INSERT INTO nba_stats.player_performance(player_id, game_id, minutes, fgm, fga, fg3m, fg3a, ftm, fta, oreb, dreb, reb, ast, blk, steals, tov, pf, pts, plus_minus, team_id) VALUES(1627936,22500001,30,3,9,2,6,0,0,0,2,2,3,1,2,0,2,8,-15,1610612760) ON CONFLICT(player_id, game_id) DO NOTHING;
        INSERT INTO nba_stats.player_performance(player_id, game_id, minutes, fgm, fga, fg3m, fg3a, ftm, fta, oreb, dreb, reb, ast, blk, steals, tov, pf, pts, plus_minus, team_id) VALUES(1630598,22500001,20,4,8,2,5,0,0,0,1,1,1,0,0,1,1,10,2,1610612760) ON CONFLICT(player_id, game_id) DO NOTHING;
        INSERT INTO nba_stats.player_performance(player_id, game_id, minutes, fgm, fga, fg3m, fg3a, ftm, fta, oreb, dreb, reb, ast, blk, steals, tov, pf, pts, plus_minus, team_id) VALUES(1631119,22500001,12,1,5,0,4,0,0,0,0,0,1,0,1,0,1,2,-3,1610612760) ON CONFLICT(player_id, game_id) DO NOTHING;
        INSERT INTO nba_stats.player_performance(player_id, game_id, minutes, fgm, fga, fg3m, fg3a, ftm, fta, oreb, dreb, reb, ast, blk, steals, tov, pf, pts, plus_minus, team_id) VALUES(1642964,22500001,2,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,-2,1610612760) ON CONFLICT(player_id, game_id) DO NOTHING;
        

        INSERT INTO nba_stats.player_performance(player_id, game_id, minutes, fgm, fga, fg3m, fg3a, ftm, fta, oreb, dreb, reb, ast, blk, steals, tov, pf, pts, plus_minus, team_id) VALUES(202710,22500002,34,7,14,1,2,16,16,2,3,5,4,1,0,1,4,31,20,1610612744) ON CONFLICT(player_id, game_id) DO NOTHING;
        INSERT INTO nba_stats.player_performance(player_id, game_id, minutes, fgm, fga, fg3m, fg3a, ftm, fta, oreb, dreb, reb, ast, blk, steals, tov, pf, pts, plus_minus, team_id) VALUES(1630228,22500002,32,6,11,4,6,1,2,3,6,9,6,1,0,2,3,17,4,1610612744) ON CONFLICT(player_id, game_id) DO NOTHING;
        INSERT INTO nba_stats.player_performance(player_id, game_id, minutes, fgm, fga, fg3m, fg3a, ftm, fta, oreb, dreb, reb, ast, blk, steals, tov, pf, pts, plus_minus, team_id) VALUES(203110,22500002,28,3,6,1,3,1,3,1,6,7,9,1,2,4,5,8,20,1610612744) ON CONFLICT(player_id, game_id) DO NOTHING;
        INSERT INTO nba_stats.player_performance(player_id, game_id, minutes, fgm, fga, fg3m, fg3a, ftm, fta, oreb, dreb, reb, ast, blk, steals, tov, pf, pts, plus_minus, team_id) VALUES(1641764,22500002,32,3,7,1,4,0,0,1,6,7,2,1,0,1,2,7,13,1610612744) ON CONFLICT(player_id, game_id) DO NOTHING;
        INSERT INTO nba_stats.player_performance(player_id, game_id, minutes, fgm, fga, fg3m, fg3a, ftm, fta, oreb, dreb, reb, ast, blk, steals, tov, pf, pts, plus_minus, team_id) VALUES(201939,22500002,32,6,14,3,9,8,8,0,1,1,4,3,1,2,3,23,1,1610612744) ON CONFLICT(player_id, game_id) DO NOTHING;
        INSERT INTO nba_stats.player_performance(player_id, game_id, minutes, fgm, fga, fg3m, fg3a, ftm, fta, oreb, dreb, reb, ast, blk, steals, tov, pf, pts, plus_minus, team_id) VALUES(1627741,22500002,22,6,11,5,10,0,0,0,1,1,0,1,0,2,0,17,5,1610612744) ON CONFLICT(player_id, game_id) DO NOTHING;
        INSERT INTO nba_stats.player_performance(player_id, game_id, minutes, fgm, fga, fg3m, fg3a, ftm, fta, oreb, dreb, reb, ast, blk, steals, tov, pf, pts, plus_minus, team_id) VALUES(1627780,22500002,12,3,6,0,1,0,0,1,1,2,1,1,1,3,3,6,3,1610612744) ON CONFLICT(player_id, game_id) DO NOTHING;
        INSERT INTO nba_stats.player_performance(player_id, game_id, minutes, fgm, fga, fg3m, fg3a, ftm, fta, oreb, dreb, reb, ast, blk, steals, tov, pf, pts, plus_minus, team_id) VALUES(201143,22500002,20,2,7,1,4,0,0,0,5,5,1,0,0,2,4,5,-10,1610612744) ON CONFLICT(player_id, game_id) DO NOTHING;
        INSERT INTO nba_stats.player_performance(player_id, game_id, minutes, fgm, fga, fg3m, fg3a, ftm, fta, oreb, dreb, reb, ast, blk, steals, tov, pf, pts, plus_minus, team_id) VALUES(1630611,22500002,2,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1610612744) ON CONFLICT(player_id, game_id) DO NOTHING;
        INSERT INTO nba_stats.player_performance(player_id, game_id, minutes, fgm, fga, fg3m, fg3a, ftm, fta, oreb, dreb, reb, ast, blk, steals, tov, pf, pts, plus_minus, team_id) VALUES(1642954,22500002,13,2,2,1,1,0,0,1,0,1,1,1,0,0,2,5,-11,1610612744) ON CONFLICT(player_id, game_id) DO NOTHING;


        INSERT INTO nba_stats.player_performance(player_id, game_id, minutes, fgm, fga, fg3m, fg3a, ftm, fta, oreb, dreb, reb, ast, blk, steals, tov, pf, pts, plus_minus, team_id) VALUES(1630559,22500002,36,9,16,1,5,7,10,1,4,5,9,0,2,5,5,26,-14,1610612747) ON CONFLICT(player_id, game_id) DO NOTHING;
        INSERT INTO nba_stats.player_performance(player_id, game_id, minutes, fgm, fga, fg3m, fg3a, ftm, fta, oreb, dreb, reb, ast, blk, steals, tov, pf, pts, plus_minus, team_id) VALUES(1629060,22500002,35,3,6,3,6,0,0,0,4,4,3,0,0,1,2,9,-6,1610612747) ON CONFLICT(player_id, game_id) DO NOTHING;
        INSERT INTO nba_stats.player_performance(player_id, game_id, minutes, fgm, fga, fg3m, fg3a, ftm, fta, oreb, dreb, reb, ast, blk, steals, tov, pf, pts, plus_minus, team_id) VALUES(1629028,22500002,33,5,7,0,0,0,2,2,4,6,0,0,1,4,3,10,-4,1610612747) ON CONFLICT(player_id, game_id) DO NOTHING;
        INSERT INTO nba_stats.player_performance(player_id, game_id, minutes, fgm, fga, fg3m, fg3a, ftm, fta, oreb, dreb, reb, ast, blk, steals, tov, pf, pts, plus_minus, team_id) VALUES(1629216,22500002,28,1,4,1,4,0,0,0,0,0,1,1,0,0,3,3,-5,1610612747) ON CONFLICT(player_id, game_id) DO NOTHING;
        INSERT INTO nba_stats.player_performance(player_id, game_id, minutes, fgm, fga, fg3m, fg3a, ftm, fta, oreb, dreb, reb, ast, blk, steals, tov, pf, pts, plus_minus, team_id) VALUES(1629029,22500002,40,17,27,2,10,7,10,0,12,12,9,2,1,3,1,43,-8,1610612747) ON CONFLICT(player_id, game_id) DO NOTHING;
        INSERT INTO nba_stats.player_performance(player_id, game_id, minutes, fgm, fga, fg3m, fg3a, ftm, fta, oreb, dreb, reb, ast, blk, steals, tov, pf, pts, plus_minus, team_id) VALUES(203935,22500002,22,3,6,0,3,3,4,0,0,0,0,1,0,3,4,9,2,1610612747) ON CONFLICT(player_id, game_id) DO NOTHING;
        INSERT INTO nba_stats.player_performance(player_id, game_id, minutes, fgm, fga, fg3m, fg3a, ftm, fta, oreb, dreb, reb, ast, blk, steals, tov, pf, pts, plus_minus, team_id) VALUES(1631222,22500002,15,2,4,1,2,0,2,2,1,3,0,0,0,0,1,5,-5,1610612747) ON CONFLICT(player_id, game_id) DO NOTHING;
        INSERT INTO nba_stats.player_performance(player_id, game_id, minutes, fgm, fga, fg3m, fg3a, ftm, fta, oreb, dreb, reb, ast, blk, steals, tov, pf, pts, plus_minus, team_id) VALUES(1629637,22500002,14,2,3,0,0,0,0,2,4,6,1,0,0,1,2,4,-6,1610612747) ON CONFLICT(player_id, game_id) DO NOTHING;
        INSERT INTO nba_stats.player_performance(player_id, game_id, minutes, fgm, fga, fg3m, fg3a, ftm, fta, oreb, dreb, reb, ast, blk, steals, tov, pf, pts, plus_minus, team_id) VALUES(1629020,22500002,11,0,4,0,2,0,0,0,3,3,0,1,0,2,0,0,-4,1610612747) ON CONFLICT(player_id, game_id) DO NOTHING;
        

        -- (note the game_id values of the 2 new games are 22500001 and 22500002).

        -- update the roster table.

        -- first, for all players already in roster table, if they are on the same team as their most recent roster entry, 
        --then just update that entry to 10-21-2025
        UPDATE nba_stats.roster AS R
        SET end_date = '2025-10-21'
        FROM (
            SELECT player_id, team_id, MAX(end_date) AS max_end_date
            FROM nba_stats.roster
            GROUP BY player_id, team_id
        ) AS latest_entry
        WHERE R.player_id = latest_entry.player_id AND R.team_id = latest_entry.team_id
            AND R.end_date = latest_entry.max_end_date
            AND (R.player_id, R.team_id) IN (

                SELECT DISTINCT player_id, team_id
                FROM nba_stats.player_performance AS PP
                WHERE PP.game_id IN ('22500002', '22500001')
            )
            AND R.end_date < '2025-10-21';


        -- if the player's most recent roster entry is a different team, then just create a new roster entry for their new team
        -- with start date 10-21-2025
        INSERT INTO nba_stats.roster(player_id, team_id, start_date, end_date)
        SELECT DISTINCT PP.player_id, PP.team_id, DATE '2025-10-21', DATE '2025-10-21'
        FROM nba_stats.player_performance AS PP
        WHERE PP.game_id IN ('22500001', '22500002') AND
            (PP.player_id, PP.team_id) NOT IN (

                SELECT player_id, team_id
                FROM nba_stats.roster
            )
        ON CONFLICT(player_id, team_id, start_date) DO NOTHING;




    COMMIT;
    """
    
    result = DB.query(query = query, connect_type = 'admin')

    print(f'result: {result}')

    if result:
        print('\n\nUPDATE SUCCESS.\n\n')
    else:
        print('\n\nUPDATE RESULT UNKNOWN.\n\n')

    DB.close()

    return result