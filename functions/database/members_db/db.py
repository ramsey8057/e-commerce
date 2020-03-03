from functions.database.db import *


def get_member(user_id):
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
    if len(row) == 0:
        return 1
    return row[0][0] + 1


def get_all_members():
    con = connect_to_db()
    row = execute_dql_query(
        con,
        'SELECT user_id, username, email, fullname, registration_date, reg_status FROM users ORDER BY user_id LIMIT 100'
    )
    return row


def del_member(user_id):
    con = connect_to_db()
    row = execute_dml_query(
        con,
        'DELETE FROM users WHERE user_id={}'.format(
            user_id
        )
    )
    return row


def get_members_count():
    con = connect_to_db()
    row = execute_dql_query(
        con,
        'SELECT COUNT(user_id) FROM users'
    )
    return row[0][0]


def get_pending_members_count():
    con = connect_to_db()
    row = execute_dql_query(
        con,
        'SELECT COUNT(user_id) FROM users WHERE reg_status = 0'
    )
    return row[0][0]


def ac_member(user_id):
    con = connect_to_db()
    row = execute_dml_query(
        con,
        'UPDATE users SET reg_status=1 WHERE user_id={}'.format(
            user_id
        )
    )
    con.commit()
    return row[0][0]


def get_latest_registered_members():
    con = connect_to_db()
    row = execute_dql_query(
        con,
        'SELECT user_id, fullname, reg_status FROM users ORDER BY user_id DESC LIMIT 5'
    )
    return row


def get_member_id(username):
    con = connect_to_db()
    row = execute_dql_query(
        con,
        'SELECT user_id FROM users WHERE username=\'{}\''.format(username)
    )
    return str(row[0][0])


def get_member_fullname(username):
    con = connect_to_db()
    row = execute_dql_query(
        con,
        'SELECT fullname FROM users WHERE username=\'{}\''.format(username)
    )
    return row[0][0]
