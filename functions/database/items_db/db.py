from functions.database.db import *


def get_new_item_id():
    con = connect_to_db()
    row = execute_dql_query(
        con,
        'SELECT item_id FROM items ORDER BY item_id DESC LIMIT 1'
    )
    con.close()
    if row == []:
        return 1
    return (row[0][0] + 1)


def get_last_5_items():
    con = connect_to_db()
    row = execute_dql_query(
        con,
        'SELECT * FROM items ORDER BY item_id DESC LIMIT 5'
    )
    con.close()
    return row
