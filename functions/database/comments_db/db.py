from functions.database.db import execute_dql_query, connect_to_db


def get_all_comments():
    con = connect_to_db()
    row = execute_dql_query(
        con,
        '''
        SELECT
            c.item_id,
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
