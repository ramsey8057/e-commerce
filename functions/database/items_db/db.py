from functions.database.db import connect_to_db, execute_dql_query, execute_dml_query


def get_new_item_id():
    con = connect_to_db()
    row = execute_dql_query(
        con,
        'SELECT item_id FROM items ORDER BY item_id DESC LIMIT 1'
    )
    if len(row) == 0:
        return 1
    return row[0][0] + 1


def get_last_5_items():
    con = connect_to_db()
    row = execute_dql_query(
        con,
        'SELECT * FROM items ORDER BY item_id DESC LIMIT 5'
    )
    return row


def get_item(item_id):
    con = connect_to_db()
    row = execute_dql_query(
        con,
        'SELECT * FROM items WHERE item_id = {}'.format(
            item_id
        )
    )
    return row


def get_all_items():
    con = connect_to_db()
    row = execute_dql_query(
        con,
        '''
        SELECT
            i.item_id,
            i.item_name,
            i.item_description,
            i.item_price,
            i.date_add,
            c.category_name,
            u.username
        FROM items as i
        JOIN categories c ON (i.category_id = c.category_id)
        JOIN users u ON (i.member_id = u.user_id)
        '''
    )
    return row


def del_item(item_id):
    con = connect_to_db()
    row = execute_dml_query(
        con,
        'DELETE FROM items WHERE item_id={}'.format(
            item_id
        )
    )
    return row


def get_items_count():
    con = connect_to_db()
    row = execute_dql_query(
        con,
        'SELECT COUNT(item_id) FROM items'
    )
    return row[0][0]


def get_item_image(item_id):
    con = connect_to_db()
    row = execute_dql_query(
        con,
        'SELECT item_image FROM items WHERE item_id={}'.format(
            item_id
        )
    )
    return row[0][0]


def set_item_image(item_id, item_image):
    con = connect_to_db()
    row = execute_dml_query(
        con,
        '''
        UPDATE
            items
        SET
            item_image='{}'
        WHERE item_id={}
        '''.format(
            item_image,
            item_id
        )
    )
    return row


def get_latest_items():
    con = connect_to_db()
    row = execute_dql_query(
        con,
        'SELECT item_id, item_name FROM items ORDER BY item_id DESC LIMIT 5'
    )
    return row
