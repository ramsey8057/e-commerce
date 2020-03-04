import os
import datetime
from flask import Blueprint, render_template, abort, redirect, url_for, request
from functions.languages.arabic import lang as ar
from functions.languages.english import lang as en
from functions.database.members_db.db import get_member_id
from functions.database.categories_db.db import get_categories_names
from functions.database.items_db.db import get_item, get_new_item_id, connect_to_db, get_all_items, del_item,\
                                            set_item_image, get_item_image
from functions.database.comments_db.db import get_item_comments
from functions.members.members import check_user
from functions.database.db import execute_dml_query

control_items = Blueprint('control_items', __name__, template_folder='templates')
images_path = 'static/data/uploads/images'


@control_items.route('/admin/items')
def items():
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
                all_items = get_all_items()
                deleted = request.args.get('deleted')
                return render_template(
                    'control_panel/items/items.html',
                    dictionary=lang,
                    session=request.cookies,
                    items=all_items,
                    deleted=deleted,
                    user_id=user_id,
                )
            elif do == 'edit':
                item_id = request.args.get('item_id')
                item_comments = get_item_comments(item_id)
                item_data = get_item(item_id)
                edit_done = request.args.get('edit_done')
                err_msg = request.args.get('err_msg')
                note = request.args.get('note')
                return render_template(
                    'control_panel/items/edit_item.html',
                    dictionary=lang,
                    session=request.cookies,
                    item_data=item_data[0],
                    edit_done=edit_done,
                    err_msg=err_msg,
                    note=note,
                    item_id=item_id,
                    categories=get_categories_names(),
                    user_id=user_id,
                    comments=item_comments
                )
            elif do == 'add':
                add_done = request.args.get('add_done')
                err_msg = request.args.get('err_msg')
                categories = get_categories_names()
                return render_template(
                    'control_panel/items/add_item.html',
                    dictionary=lang,
                    session=request.cookies,
                    add_done=add_done,
                    err_msg=err_msg,
                    categories=categories,
                    user_id=user_id,
                )
            elif do == 'delete':
                return redirect(
                    url_for(
                        '.delete_item',
                        item_id=request.args.get('item_id')
                    ),
                )
            elif do == 'approve':
                pass
            else:
                return redirect(url_for('.items'))
        else:
            return redirect('/admin')
    except Exception as e:
        print(e)
        return redirect('/admin')


@control_items.route('/admin/items/add_item', methods=['POST'])
def add_item():
    username = request.cookies.get('username')
    password = request.cookies.get('password')
    language = request.cookies.get('language')
    item_id = get_new_item_id()
    if language == 'ar':
        lang = ar
    else:
        lang = en
    try:
        if check_user(username, password):
            # fetch the data from the request
            item_name = request.form.get('name')
            item_description = request.form.get('description')
            item_price = request.form.get('price')
            country_of_manufacture = request.form.get('country_of_manufacture')
            item_image = request.files.get('image')
            item_status = request.form.get('status')
            category_id = request.form.get('category')
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
            name_array = item_image.filename.split('.')
            file_extension = name_array[len(name_array) - 1]
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
                    get_member_id(username),
                )
            )
            # save image to files
            item_image.save(image_path)
            # close the connection
            if rowcount >= 1:
                return redirect(url_for('.items', do='add', add_done=True))
            else:
                return redirect(url_for('.items', do='add', add_done=False))
        else:
            return redirect('/admin')
    except Exception as e:
        e = str(e)
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


@control_items.route('/admin/items/edit_item', methods=['POST'])
def edit_item():
    current_username = request.cookies.get('username')
    current_password = request.cookies.get('password')
    language = request.cookies.get('language')
    if language == 'ar':
        lang = ar
    else:
        lang = en
    try:
        if check_user(current_username, current_password):
            # fetch the data from the request
            name = request.form.get('name')
            description = request.form.get('description')
            price = request.form.get('price')
            country_of_manufacture = request.form.get('country_of_manufacture')
            image = request.files.get('image')
            status = request.form.get('status')
            category = request.form.get('category')
            item_id = request.form.get('id')
            # validate the inputs
            if status == 0:
                raise Exception('invalid item status')
            else:
                if image is not None:
                    if 'image' in str(image.content_type):
                        # change the picture name to a unique one
                        name_array = image.filename.split('.')
                        file_extension = name_array[len(name_array) - 1]
                        image.filename = 'item_{}_image.{}'.format(item_id, file_extension)
                        # create the image path
                        image_path = os.path.join(images_path, image.filename)
                        # delete the old image
                        os.remove(os.path.join(os.getcwd(), get_item_image(item_id)))
                        # set the new item image
                        print(set_item_image(item_id, image_path))
                        # save image to files
                        image.save(os.path.join(os.getcwd(), image_path))
                        try:
                            price = int(price)
                        except Exception as e:
                            print(e)
                            raise Exception('invalid item price')
                    else:
                        raise Exception('invalid item image')
                else:
                    try:
                        price = int(price)
                    except Exception as e:
                        print(e)
                        raise Exception('invalid item price')
            # connect to the database and insert the category
            con = connect_to_db()
            rowcount = execute_dml_query(
                con,
                '''
                UPDATE
                    items
                SET
                    item_name='{}',
                    item_description='{}',
                    item_price={},
                    country_of_manufacture='{}',
                    item_status='{}',
                    category_id={}
                WHERE item_id={}
                '''.format(
                    name,
                    description,
                    price,
                    country_of_manufacture,
                    status,
                    category,
                    item_id
                )
            )
            # close the database connection
            if rowcount >= 1:
                return redirect(
                    url_for(
                        '.items',
                        do='edit',
                        edit_done=True,
                        item_id=item_id
                    )
                )
            else:
                return redirect(
                    url_for(
                        '.items',
                        do='edit',
                        edit_done=False,
                        item_id=item_id
                    )
                )
        else:
            return redirect('/admin')
    except Exception as e:
        e = str(e)
        print(e)
        if 'already exists' in e:
            return redirect(url_for('.items', do='add', add_done=False))
        else:
            if 'invalid item status' in e:
                return redirect(
                    url_for(
                        '.items',
                        do='edit',
                        edit_done=False,
                        err_msg=lang['ITEM_STATUS_ERR_MSG']
                    )
                )
            elif 'invalid item price' in e:
                return redirect(
                    url_for(
                        '.items',
                        do='edit',
                        edit_done=False,
                        err_msg=lang['ITEM_PRICE_ERR_MSG']
                    )
                )
            elif 'invalid item image' in e:
                return redirect(
                    url_for(
                        '.items',
                        do='edit',
                        edit_done=False,
                        err_msg=lang['ITEM_IMAGE_ERR_MSG']
                    )
                )
            # TODO: redirect to the 503 page
            return abort(503)


@control_items.route('/admin/items/delete/<item_id>')
def delete_item(item_id):
    try:
        username = request.cookies.get('username')
        password = request.cookies.get('password')
        if check_user(username, password):
            row = del_item(item_id)
            return redirect(url_for('.items', deleted=row))
        else:
            return redirect(url_for('index'))
    except Exception as e:
        print(e)
        return redirect(url_for('.items'))
