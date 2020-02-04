from flask import Blueprint, render_template, abort, redirect, url_for, request, session
from functions.languages.english import lang as en
from functions.languages.arabic import lang as ar
from functions.database.db import *

control_categories = Blueprint('control_categories', __name__, template_folder='templates')

@control_categories.route('/admin/categories')
def categories():
    try:
        if session['username'] != '' and session['password'] != '':
            lang = None
            if session['language'] == 'ar':
                lang = ar
            else:
                lang = en
            do = request.args.get('do')
            if do == None:
                categories = get_all_categories()
                deleted = request.args.get('deleted')
                return render_template(
                    'control_panel/categories/categories.html',
                    dictionary=lang,
                    session=session,
                    categories=categories,
                    deleted=deleted
                )
            elif do == 'edit':
                pass
            elif do == 'add':
                add_done = request.args.get('add_done')
                err_msg = request.args.get('err_msg')
                return render_template(
                    'control_panel/categories/add_category.html',
                    dictionary=lang,
                    session=session,
                    add_done=add_done,
                    err_msg=err_msg,
                )
            elif do == 'delete':
                pass
            else:
                return redirect(url_for('.categories'))
        else:
            return redirect('/admin')
    except:
        try:
            return redirect('/admin')
        except:
            # TODO: redirect to the 404 page
            abort(404)

@control_categories.route('/admin/categories/add_category', methods=['POST',])
def add_category():
    if request.method == 'POST':
        category_id = get_new_category_id()
        name = ''
        description = ''
        order = ''
        is_visible = 1
        allow_comments = 1
        allow_ads = 1
        try:
            # fetch the data from the request
            name = request.form['name']
            description = request.form['description']
            order = request.form['order']
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
                    except:
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
            con.close()
            if rowcount >= 1:
                return redirect(url_for('.categories', do='add', add_done=True))
            else:
                return redirect(url_for('.categories', do='add', add_done=False))
        except Exception as e:
            e = str(e)
            lang = None
            if session['language'] == 'ar':
                lang = ar
            else:
                lang = en
            if 'already exists' in e:
                if 'category_name' in e:
                    return redirect(url_for('.categories', do='add', add_done=False,
                                            err_msg='{} "{}" {}'.format(lang['CATEGORY'], name,
                                                                        lang['NOT_AVAILABLE'])))
                elif 'category_order' in e:
                    return redirect(url_for('.categories', do='add', add_done=True,
                                            err_msg='{} "{}" {}'.format(lang['CATEGORY_ORDER', order,
                                                                        lang['NOT_AVAILABLE']])))
            else:
                if e == 'invalid category name':
                    return redirect(url_for('.categories', do='add', add_done=False, err_msg=lang['CATEGORY_NAME_ERR_MSG']))
                elif e == 'invalid category description':
                    return redirect(url_for('.categories', do='add', add_done=False, err_msg=lang['CATEGORY_DESCRIPTION_ERR_MSG']))
                elif e == 'invalid category order':
                    return redirect(url_for('.categories', do='add', add_done=False, err_msg=lang['CATEGORY_ORDER_ERR_MSG']))
            # TODO: redirect to the 503 page
            return abort(503)
