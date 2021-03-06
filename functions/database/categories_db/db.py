from functions.database.db import *


def get_new_category_id():
    con = connect_to_db()
    row = execute_dql_query(
        con,
        'SELECT category_id FROM categories ORDER BY category_id DESC LIMIT 1'
    )
    if row is []:
        return 1
    return row[0][0] + 1


def get_all_categories(sort):
    con = connect_to_db()
    row = execute_dql_query(
        con,
        'SELECT * FROM categories ORDER BY category_order {} LIMIT 100'.format(sort)
    )
    return row


def get_categories_count():
    con = connect_to_db()
    row = execute_dql_query(
        con,
        'SELECT COUNT(category_id) FROM categories'
    )
    return row[0][0]


def get_category_data(category_id):
    con = connect_to_db()
    row = execute_dql_query(
        con,
        'SELECT * FROM categories WHERE category_id={}'.format(
            category_id,
        )
    )
    return row[0]


def del_category(category_id):
    con = connect_to_db()
    row = execute_dml_query(
        con,
        'DELETE FROM categories WHERE category_id={}'.format(
            category_id
        )
    )
    return row


def get_categories_names():
    con = connect_to_db()
    row = execute_dql_query(
        con,
        'SELECT category_id, category_name FROM categories ORDER BY category_order'
    )
    return row
