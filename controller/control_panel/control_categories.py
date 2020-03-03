from flask import Blueprint, render_template, abort, redirect, url_for, request
from functions.languages.english import lang as en
from functions.languages.arabic import lang as ar
from functions.database.db import connect_to_db, execute_dml_query
from functions.database.categories_db.db import get_all_categories, get_new_category_id, get_category_data, del_category
from functions.members.members import check_user
from functions.database.members_db.db import get_member_id

control_categories = Blueprint('control_categories', __name__, template_folder='templates')


@control_categories.route('/admin/categories')
def categories():
    user_id = get_member_id(request.cookies.get('username'))
    try:
        username = request.cookies.get('username')
        password = request.cookies.get('password')
        if check_user(username, password):
            language = request.cookies.get('language')
            if language == 'ar':
                lang = ar
            else:
                lang = en
            do = request.args.get('do')
            if do is None:
                sort = request.args.get('sort')
                if sort != 'ASC' and sort != 'DESC':
                    sort = 'ASC'
                deleted = request.args.get('deleted')
                return render_template(
                    'control_panel/categories/categories.html',
                    dictionary=lang,
                    session=request.cookies,
                    categories=get_all_categories(sort),
                    deleted=deleted,
                    sort=sort,
                    user_id=user_id
                )
            elif do == 'edit':
                category_id = request.args.get('category_id')
                category_data = get_category_data(category_id)
                edit_done = request.args.get('edit_done')
                err_msg = request.args.get('err_msg')
                return render_template(
                    'control_panel/categories/edit_category.html',
                    dictionary=lang,
                    category_id=category_id,
                    category_data=category_data,
                    edit_done=edit_done,
                    err_msg=err_msg,
                    user_id=user_id,
                    session=request.cookies
                )
            elif do == 'add':
                add_done = request.args.get('add_done')
                err_msg = request.args.get('err_msg')
                return render_template(
                    'control_panel/categories/add_category.html',
                    dictionary=lang,
                    session=request.cookies,
                    add_done=add_done,
                    err_msg=err_msg,
                    user_id=user_id
                )
            elif do == 'delete':
                return redirect(url_for('.delete_category', category_id=request.args.get('category_id')))
            else:
                return redirect(url_for('.categories'))
        else:
            return redirect('/admin')
    except Exception as e:
        print(e)
        return redirect('/admin')


@control_categories.route('/admin/categories/add_category', methods=['POST'])
def add_category():
    username = request.cookies.get('username')
    password = request.cookies.get('password')
    language = request.cookies.get('language')
    if language == 'ar':
        lang = ar
    else:
        lang = en
    category_id = get_new_category_id()
    name = None
    order = None
    try:
        if check_user(username, password):
            # fetch the data from the request
            name = request.form.get('name')
            description = request.form.get('description')
            order = request.form.get('order')
            is_visible = request.form.get('is_visible')
            allow_comments = request.form.get('allow_comments')
            allow_ads = request.form.get('allow_ads')
            # validate the inputs
            if is_visible != 'on':
                is_visible = 0
            else:
                is_visible = 1
            if allow_comments != 'on':
                allow_comments = 0
            else:
                allow_comments = 1
            if allow_ads != 'on':
                allow_ads = 0
            else:
                allow_ads = 1
            if len(name) > 50:
                raise Exception('invalid category name')
            else:
                if len(description) > 220:
                    raise Exception('invalid category description')
                else:
                    try:
                        order = int(order)
                    except Exception as e:
                        print(e)
                        raise Exception('invalid category order')
            # connect to the database and insert the category
            con = connect_to_db()
            rowcount = execute_dml_query(
                con,
                '''
                INSERT INTO categories (
                    category_id,
                    category_name,
                    category_description,
                    category_order,
                    category_visibility,
                    category_allow_comment,
                    category_allow_ads
                )
                VALUES (
                    {},
                    '{}',
                    '{}',
                    {},
                    {},
                    {},
                    {}
                )
                '''.format(
                    category_id,
                    name,
                    description,
                    order,
                    is_visible,
                    allow_comments,
                    allow_ads
                )
            )
            # close the connection
            if rowcount >= 1:
                return redirect(url_for('.categories', do='add', add_done=True))
            else:
                return redirect(url_for('.categories', do='add', add_done=False))
        else:
            return redirect('/admin')
    except Exception as e:
        e = str(e)
        if 'already exists' in e:
            if 'category_name' in e:
                return redirect(
                    url_for(
                        '.categories',
                        do='add',
                        add_done=False,
                        err_msg='{} "{}" {}'.format(
                            lang['CATEGORY'],
                            name,
                            lang['NOT_AVAILABLE']
                        )
                    )
                )
            elif 'category_order' in e:
                return redirect(
                    url_for(
                        '.categories',
                        do='add',
                        add_done=False,
                        err_msg='{} "{}" {}'.format(
                            lang['CATEGORY_ORDER'],
                            order,
                            lang['NOT_AVAILABLE']
                        )
                    )
                )
        else:
            if e == 'invalid category name':
                return redirect(
                    url_for(
                        '.categories',
                        do='add',
                        add_done=False,
                        err_msg=lang['CATEGORY_NAME_ERR_MSG']
                    )
                )
            elif e == 'invalid category description':
                return redirect(
                    url_for(
                        '.categories',
                        do='add',
                        add_done=False,
                        err_msg=lang['CATEGORY_DESCRIPTION_ERR_MSG']
                    )
                )
            elif e == 'invalid category order':
                return redirect(
                    url_for(
                        '.categories',
                        do='add',
                        add_done=False,
                        err_msg=lang['CATEGORY_ORDER_ERR_MSG']
                    )
                )
            # TODO: redirect to the 503 page
            return abort(503)


@control_categories.route('/admin/categories/edit_category', methods=['POST'])
def edit_category():
    username = request.cookies.get('username')
    password = request.cookies.get('password')
    language = request.cookies.get('language')
    category_name = None
    category_order = None
    category_id = None
    if language == 'ar':
        lang = ar
    else:
        lang = en
    try:
        if check_user(username, password):
            # fetch the data from the request
            category_id = request.form.get('category_id')
            category_name = request.form.get('name')
            category_description = request.form.get('description')
            category_order = request.form.get('order')
            is_visible = request.form.get('is_visible')
            allow_comments = request.form.get('allow_comments')
            allow_ads = request.form.get('allow_ads')
            # validate the inputs
            if is_visible != 'on':
                is_visible = 0
            else:
                is_visible = 1
            if allow_comments != 'on':
                allow_comments = 0
            else:
                allow_comments = 1
            if allow_ads != 'on':
                allow_ads = 0
            else:
                allow_ads = 1
            if len(category_name) > 50:
                raise Exception('invalid category name')
            else:
                if len(category_description) > 220:
                    raise Exception('invalid category description')
                else:
                    try:
                        category_order = int(category_order)
                    except Exception as e:
                        print(e)
                        raise Exception('invalid category order')
            # connect to the database and insert the category
            con = connect_to_db()
            rowcount = execute_dml_query(
                con,
                '''
                UPDATE
                    categories
                SET
                    category_name='{}',
                    category_description='{}',
                    category_order={},
                    category_visibility={},
                    category_allow_comment={},
                    category_allow_ads={}
                WHERE category_id={}
                '''.format(
                    category_name,
                    category_description,
                    category_order,
                    is_visible,
                    allow_comments,
                    allow_ads,
                    category_id,
                )
            )
            # close the database connection
            if rowcount >= 1:
                return redirect(
                    url_for(
                        '.categories',
                        do='edit',
                        edit_done=True,
                        category_id=category_id
                    )
                )
            else:
                return redirect(
                    url_for(
                        '.categories',
                        do='edit',
                        edit_done=False,
                        category_id=category_id
                    )
                )
        else:
            return redirect('/admin')
    except Exception as e:
        e = str(e)
        if 'already exists' in e:
            if 'category_name' in e:
                return redirect(
                    url_for(
                        '.categories',
                        do='edit',
                        edit_done=False,
                        category_id=category_id,
                        err_msg='{} "{}" {}'.format(
                            lang['CATEGORY'],
                            category_name,
                            lang['NOT_AVAILABLE']
                        )
                    )
                )
            elif 'category_order' in e:
                return redirect(
                    url_for(
                        '.categories',
                        do='edit',
                        edit_done=False,
                        category_id=category_id,
                        err_msg='{} "{}" {}'.format(
                            lang['CATEGORY_ORDER'],
                            category_order,
                            lang['NOT_AVAILABLE']
                        )
                    )
                )
        else:
            if e == 'invalid category name':
                return redirect(
                    url_for(
                        '.categories',
                        do='edit',
                        edit_done=False,
                        err_msg=lang['CATEGORY_NAME_ERR_MSG']
                    )
                )
            elif e == 'invalid category description':
                return redirect(
                    url_for(
                        '.categories',
                        do='edit',
                        edit_done=False,
                        err_msg=lang['CATEGORY_DESCRIPTION_ERR_MSG']
                    )
                )
            elif e == 'invalid category order':
                return redirect(
                    url_for(
                        '.categories',
                        do='edit',
                        edit_done=False,
                        err_msg=lang['CATEGORY_ORDER_ERR_MSG']
                    )
                )
            # TODO: redirect to the 503 page
            return abort(503)


@control_categories.route('/admin/category/delete/<category_id>')
def delete_category(category_id):
    try:
        username = request.cookies.get('username')
        password = request.cookies.get('password')
        if check_user(username, password):
            row = del_category(category_id)
            return redirect(url_for('.categories', deleted=row))
        else:
            return redirect('/admin')
    except Exception as e:
        print(e)
        return redirect('/admin')
