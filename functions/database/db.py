import psycopg2

def connect_to_db():
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
    return rows # gonna return array of tubles

def execute_dml_query(con, query):
    cur = con.cursor()
    cur.execute(query)
    con.commit()
    return cur.rowcount

def get_user(user_id):
    con = connect_to_db()
    row = execute_dql_query(
        con,
        'SELECT * FROM users WHERE user_id = {}'.format(
            user_id,
        )
    )
    return row[0]
