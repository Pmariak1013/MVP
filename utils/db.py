import psycopg2
from dotenv import load_dotenv
import os
import logging
from utils.user_session import session

class DB:
    def __init__(self):
        self.conn = None
        self.conn_type = None
        load_dotenv()



    # function to connect to DB with admin username and password (granted all privileges on DB)
    def connect_admin(self):
        logging.debug(f'\n\n\n[DEBUG] (db.py):  attempting connection as admin\n\n\n')
        if self.conn is not None and self.conn_type == 'admin':
            logging.debug(f'\n\n\n[DEBUG] (db.py):  reusing existing admin connection\n\n\n')
            return self.conn
        elif self.conn_type == 'standard_user':
            logging.debug(f'\n\n\n[DEBUG] (db.py):  closing existing standard_user connection before connecting as admin\n\n\n')
            self.close()
        try:
            self.conn = psycopg2.connect(
                dbname=os.getenv("DB_NAME"),
                user=os.getenv("DB_ADMIN_USER"),
                password=os.getenv("DB_ADMIN_USER_PASSWORD"),
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT")
            )
            logging.debug(f'\n\n\n[DEBUG] (db.py):  successfully connected as admin\n\n\n')
            self.conn_type = 'admin'
            return self.conn
        
        except Exception as e:
            print(f"Error connecting to database: {e}")
        return None
    




    # connect as standard_user to postgres server (only has SELECT privileges on tables of DB)
    def connect_standard_user(self):
        logging.debug(f'\n\n\n[DEBUG] (db.py):  Connecting as standard_user\n\n\n')
        if self.conn is not None and self.conn_type == 'standard_user':
            logging.debug(f'\n\n\n[DEBUG] (db.py):  reusing existing standard_user connection\n\n\n')
            return self.conn
        elif self.conn_type == 'admin':
            logging.debug(f'\n\n\n[DEBUG] (db.py):  closing existing admin connection before connecting as standard_user\n\n\n')
            self.close()
        try:
            self.conn = psycopg2.connect(
                dbname=os.getenv("DB_NAME"),
                user=os.getenv("DB_STANDARD_USER"),
                password=os.getenv("DB_STANDARD_USER_PASSWORD"),
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT")
            )
            logging.debug(f'\n\n\n[DEBUG] (db.py):  successfully connected as standard_user\n\n\n')
            self.conn_type = 'standard_user'
            return self.conn
        
        except Exception as e:
            print(f"Error connecting to database: {e}")
        return None
    




    def is_empty(self,table):
        return self.sizeOf(table)==0

    def sizeOf(self,table):
        self.connect_admin()
        
        with self.conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) FROM {table}")
            return cur.fetchone()[0]
    
    def getCols(self, table):
        self.connect_admin()
        if self.conn is None:
            print("No database connection available.")
            return []
        
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT column_name, data_type, character_maximum_length
                FROM information_schema.columns
                WHERE table_name = %s
                ORDER BY ordinal_position;
                """, (table,)
            )
            return cur.fetchall()





    def query(self, query, connect_type='admin', params=None):
        logging.debug(f'\n\n\n[DEBUG] (db.py):  DB.query called with connect_type={connect_type}\n\n\n')
        #self.connect()


        #if self.conn is None:
            #print(f'\n\n\n[DEBUG] (db.py):  no connection, creating one now based on given type\n\n\n')
        if connect_type == 'standard_user':
            logging.debug(f'\n\n\n[DEBUG] (db.py):  Connecting as standard_user\n\n\n')
            self.connect_standard_user()
        elif connect_type == 'admin':
            logging.debug(f'\n\n\n[DEBUG] (db.py):  Connecting as admin\n\n\n')
            self.connect_admin()
        else:
            logging.debug(f'\n\n\n[DEBUG] (db.py):  Invalid connect_type provided: {connect_type}\nQuery: {query}\n\n')
            return False

        if self.conn is None:
            print("No database connection available.")
            return []

        try:
            logging.debug(f'\n\n\n[DEBUG] (db.py):  Executing query in try statement..\n\n\n')
            with self.conn.cursor() as cur:
                cur.execute(query, params)
                if query.strip().upper().startswith("SELECT"):
                    results = cur.fetchall()
                    headers = [desc[0] for desc in cur.description]
                    logging.debug(f'\n\n\n[DEBUG] (db.py):  SELECT Query returned.\n\n\n')
                    return results, headers
            
                self.conn.commit()
                logging.debug(f'\n\n\n[DEBUG] (db.py):  Query executed and committed successfully.\n\n\n')
                return True
        except Exception as e:
            logging.debug(f'\n\n\n[DEBUG] (db.py):  Exception occurred during query execution: {e}\n\n\n')
            msg = str(e)
            if self.conn:
                self.conn.rollback()

            if "unique" in msg.lower() or "duplicate key" in msg.lower():
                return "UNIQUE_VIOLATION"
            
            print(e)
            return False










    def close(self):
        if self.conn is not None:
            self.conn.close()
            self.conn = None

    def convert_value(self, val, sql_type):
        if val == "" or val.lower() == "null":
            return None

        if sql_type in ("integer", "bigint", "smallint", "serial"):
            return int(val)

        if sql_type in ("varchar", "character varying", "char", "character", "text"):
            return val

        if sql_type.startswith("numeric") or sql_type.startswith("decimal"):
        # PostgreSQL stores DECIMAL(6,2) as a numeric type
            from decimal import Decimal
            return Decimal(val)

        if sql_type in ("date",):
            from datetime import datetime
            return datetime.strptime(val, "%Y-%m-%d").date()

        # default: treat as string
        return val

    def python_convert(self, sql_type):
        if sql_type in ("character varying", "character", "text"):
            return "STRING"
        if sql_type in ("integer", "smallint", "bigint"):
            return "INT"
        if sql_type in ("numeric", "decimal"):
            return "DECIMAL"
        if sql_type == "date":
            return "DATE (YYYY-MM-DD)"
        return "STRING"
    
DB = DB()