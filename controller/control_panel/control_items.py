import os
import datetime
from flask import Blueprint, render_template, abort, redirect, url_for, request, session
from functions.languages.arabic import lang as ar
from functions.languages.english import lang as en
from functions.database.members_db.db import get_member_id
from functions.database.categories_db.db import get_categories_names
from functions.database.items_db.db import *

control_items = Blueprint('control_items', __name__, template_folder='templates')
images_path = 'static/data/uploads/images'


@control_items.route('/admin/items')
def items():
    user_id = get_member_id(request.cookies.get('username'))
    try:
        if session['username'] != '' and session['password'] != '':
            if session['language'] == 'ar':
                lang = ar
            else:
                lang = en
            do = request.args.get('do')
            if do is None:
                return 'Welcome to items page'
            elif do == 'edit':
                pass
            elif do == 'add':
                add_done = request.args.get('add_done')
                err_msg = request.args.get('err_msg')
                categories = get_categories_names()
                return render_template(
                    'control_panel/items/add_item.html',
                    dictionary=lang,
                    session=session,
                    add_done=add_done,
                    err_msg=err_msg,
                    categories=categories,
                    user_id=user_id,
                )
            elif do == 'delete':
                pass
            elif do == 'approve':
                pass
            else:
                return redirect(url_for('.items'))
    except Exception as e:
        print(e)
        try:
            return redirect('/admin')
        except Exception as e:
            print(e)
            # TODO: redirect to the 404 page
            abort(404)


@control_items.route('/admin/items/add_item', methods=['POST'])
def add_item():
    if request.method == 'POST':
        item_id = get_new_item_id()
        try:
            # fetch the data from the request
            item_name = request.form['name']
            item_description = request.form['description']
            item_price = request.form['price']
            country_of_manufacture = request.form['country_of_manufacture']
            item_image = request.files['image']
            item_status = request.form['status']
            category_id = request.form['category']
            # validate the inputs
            if item_status == 0:
                raise Exception('invalid item status')
            else:
                if 'image' in str(item_image.content_type):
                    try:
                        item_price = int(item_price)
                    except Exception as e:
                        print(e)
                        raise Exception('invalid item price')
                else:
                    raise Exception('invalid item image')
            # change the picture name to a unique one
            splitted_name = item_image.filename.split('.')
            file_extension = splitted_name[len(splitted_name) - 1]
            item_image.filename = 'item_{}_image.{}'.format(item_id, file_extension)
            # create the image path
            image_path = os.path.join(images_path, item_image.filename)
            # connect to the database and insert the item
            con = connect_to_db()
            rowcount = execute_dml_query(
                con,
                '''
                INSERT INTO items (
                    item_id,
                    item_name,
                    item_description,
                    item_price,
                    date_add,
                    country_of_manufacture,
                    item_image,
                    item_status,
                    category_id,
                    member_id
                )
                VALUES (
                    {},
                    '{}',
                    '{}',
                    {},
                    '{}',
                    '{}',
                    '{}',
                    '{}',
                    {},
                    {}
                )
                '''.format(
                    item_id,
                    item_name,
                    item_description,
                    item_price,
                    '{} - {} - {}'.format(
                        datetime.datetime.now().day,
                        datetime.datetime.now().month,
                        datetime.datetime.now().year,
                    ),
                    country_of_manufacture,
                    image_path,
                    item_status,
                    category_id,
                    get_member_id(session['username']),
                )
            )
            # save image to files
            item_image.save(image_path)
            # close the connection
            con.close()
            if rowcount >= 1:
                return redirect(url_for('.items', do='add', add_done=True))
            else:
                return redirect(url_for('.items', do='add', add_done=False))
        except Exception as e:
            e = str(e)
            if session['language'] == 'ar':
                lang = ar
            else:
                lang = en
            if 'already exists' in e:
                return redirect(url_for('.items', do='add', add_done=False))
            elif 'invalid item status' in e:
                return redirect(
                    url_for(
                        '.items',
                        do='add',
                        add_done=False,
                        err_msg=lang['INVALID_ITEM_STATUS_ERR_MSG']
                    )
                )
            elif 'invalid item price' in e:
                return redirect(url_for('.items', do='add', add_done=False, err_msg=lang['INVALID_ITEM_PRICE_ERR_MSG']))
            elif 'invalid item image' in e:
                return redirect(url_for('.items', do='add', add_done=False, err_msg=lang['INVALID_ITEM_IMAGE_ERR_MSG']))
            else:
                return redirect(url_for('.items'))
    else:
        return redirect(url_for('.members'))
