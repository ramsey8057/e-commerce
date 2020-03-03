import psycopg2
from general_vars.con import get_con


def connect_to_db():
    return get_con()


def create_new_connection():
    # connect to database
    con = psycopg2.connect(
        host='rajje.db.elephantsql.com',
        database='mhqvluwu',
        user='mhqvluwu',
        password='SoaOFudyzAgBywON6U3P6vIq02kyC5J5',
    )
    return con


def execute_dql_query(con, query):
    # create a cursor
    cur = con.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    return rows  # gonna return array of tuples


def execute_dml_query(con, query):
    cur = con.cursor()
    cur.execute(query)
    con.commit()
    return cur.rowcount
