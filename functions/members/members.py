from functions.database.db import connect_to_db, execute_dml_query, execute_dql_query


def check_user_for_log_in(username, password):
    try:
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
        execute_dml_query(
            con,
            '''
            UPDATE
                users
            SET
                is_logged_in = 1
            WHERE
                username = '{}' AND
                password = '{}'
            '''.format(
                username,
                password
            )
        )
        if len(row) == 0:
            return False
        else:
            return True
    except Exception as e:
        print(e)
        return False


def check_user(username, password):
    try:
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
                is_logged_in = 1
            '''.format(
                username,
                password
            )
        )
        if len(row) == 0:
            return False
        else:
            return True
    except Exception as e:
        print(e)
        return False


def logout_from_all(username):
    try:
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
        return True
    except Exception as e:
        print(e)
        return False
