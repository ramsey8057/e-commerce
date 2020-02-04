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

def get_new_member_id():
    con = connect_to_db()
    row = execute_dql_query(
        con,
        'SELECT user_id FROM users ORDER BY user_id DESC LIMIT 1'
    )
    con.close()
    if row == []:
        return 1
    return (row[0][0] + 1)

def get_all_users():
    con = connect_to_db()
    row = execute_dql_query(
        con,
        'SELECT user_id, username, email, fullname, registration_date, reg_status FROM members ORDER BY user_id LIMIT 100'
    )
    con.close()
    return row

def del_member(user_id):
    con = connect_to_db()
    row = execute_dml_query(
        con,
        'DELETE FROM users WHERE user_id={}'.format(
            user_id
        )
    )
    con.close()
    return row

def get_users_count():
    con = connect_to_db()
    row = execute_dql_query(
        con,
        'SELECT COUNT(user_id) FROM users'
    )
    con.close()
    return row[0][0]

def get_pending_users_count():
    con = connect_to_db()
    row = execute_dql_query(
        con,
        'SELECT COUNT(user_id) FROM users WHERE reg_status = 0'
    )
    con.close()
    return row[0][0]

def ac_member(user_id):
    con = connect_to_db()
    row = execute_dml_query(
        con,
        'UPDATE members SET reg_status=1 WHERE user_id={}'.format(
            user_id
        )
    )
    con.commit()
    con.close()
    return row[0][0]

def get_latest_registerd_users():
    con = connect_to_db()
    row = execute_dql_query(
        con,
        'SELECT user_id, fullname, reg_status FROM users ORDER BY user_id LIMIT 5'
    )
    con.close()
    return row

def get_new_category_id():
    con = connect_to_db()
    row = execute_dql_query(
        con,
        'SELECT category_id FROM categories ORDER BY category_id DESC LIMIT 1'
    )
    con.close()
    if row == []:
        return 1
    return (row[0][0] + 1)
