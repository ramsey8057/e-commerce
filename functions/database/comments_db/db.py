from functions.database.db import execute_dql_query, connect_to_db, execute_dml_query


def get_all_comments():
    con = connect_to_db()
    row = execute_dql_query(
        con,
        '''
        SELECT
            c.comment_id,
            c.comment,
            i.item_name,
            u.username,
            c.comment_date
        FROM comments as c
        JOIN items as i ON (c.item_id = c.item_id)
        JOIN users as u ON (u.user_id = c.user_id)
        '''
    )
    return row


def del_comment(comment_id):
    con = connect_to_db()
    row = execute_dml_query(
        con,
        'DELETE FROM comments WHERE comment_id={}'.format(
            comment_id
        )
    )
    return row


def get_comments_count():
    con = connect_to_db()
    row = execute_dql_query(
        con,
        'SELECT COUNT(comment_id) FROM comments'
    )
    return row[0][0]


def get_comment(comment_id):
    con = connect_to_db()
    row = execute_dql_query(
        con,
        'SELECT comment_id, comment FROM comments WHERE comment_id={}'.format(
            comment_id
        )
    )
    return row


def get_item_comments(item_id):
    con = connect_to_db()
    row = execute_dql_query(
        con,
        '''
        SELECT
            c.comment_id,
            c.comment,
            u.username,
            c.comment_date
        FROM comments c
        join users u ON (c.user_id = u.user_id)
        WHERE c.item_id = {}
        '''.format(
            item_id
        )
    )
    return row


def get_latest_comments():
    con = connect_to_db()
    row = execute_dql_query(
        con,
        '''
        SELECT
            u.user_id,
            c.comment_id,
            u.username,
            c.comment
        FROM comments c
        JOIN users u ON (c.user_id = u.user_id)
        LIMIT 5
        '''
    )
    return row
