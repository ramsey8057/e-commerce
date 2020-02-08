from functions.database.db import *
from flask import make_response


def check_user(username, password, language):
    con = connect_to_db()
    row = execute_dql_query(
        con,
        '''
        SELECT
            username,
            password
        FROM
            users
        WHERE
            username = '{}' AND
            password = '{}' AND
            reg_status = 1 AND
            group_id = 1 AND
            is_logged_in = 0
        '''.format(
            username,
            password
        )
    )
    con.close()
    if row.count == 0:
        return False
    else:
        response = make_response('new response')
        response.set_cookie('ramsey-e-commerce-username', row[0][0])
        response.set_cookie('ramsey-e-commerce-password', row[0][1])
        response.set_cookie('ramsey-e-commerce-language', language)
        return True


def logout_from_all(username):
    con = connect_to_db()
    execute_dml_query(
        con,
        '''
        UPDATE
            users
        SET is_logged_in = 0
        WHERE
            username = '{}'
        '''.format(
            username
        )
    )
    con.close()
    response = make_response('new response')
    response.set_cookie('ramsey-e-commerce-username', None)
    response.set_cookie('ramsey-e-commerce-password', None)
    response.set_cookie('ramsey-e-commerce-language', None)
