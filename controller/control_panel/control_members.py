import hashlib
import datetime
from flask import Blueprint, render_template, abort, redirect, url_for, request, make_response
from functions.languages.english import lang as en
from functions.languages.arabic import lang as ar
from functions.database.db import connect_to_db, execute_dml_query, execute_dql_query
from functions.database.items_db.db import get_items_count
from functions.database.members_db.db import get_member_id, get_all_members, get_member, get_new_member_id, ac_member, del_member
from functions.members.members import check_user

control_members = Blueprint('control_members', __name__, template_folder='templates')


@control_members.route('/admin/members')
def members():
    try:
        username = request.cookies.get('username')
        password = request.cookies.get('password')
        language = request.cookies.get('language')
        user_id = get_member_id(request.cookies.get('username'))
        if check_user(username, password):
            if language == 'ar':
                lang = ar
            else:
                lang = en
            do = request.args.get('do')
            if do is None:
                users = get_all_members()
                deleted = request.args.get('deleted')
                activated = request.args.get('activated')
                return render_template(
                    'control_panel/members/members.html',
                    dictionary=lang,
                    session=request.cookies,
                    users=users,
                    deleted=deleted,
                    activated=activated,
                    pending=False,
                    user_id=user_id,
                )
            elif do == 'add':
                add_done = request.args.get('add_done')
                err_msg = request.args.get('err_msg')
                note = request.args.get('note')
                return render_template(
                    'control_panel/members/add_member.html',
                    dictionary=lang,
                    add_done=add_done,
                    err_msg=err_msg,
                    note=note,
                    user_id=user_id,
                    session=request.cookies
                )
            elif do == 'edit':
                user_id = request.args.get('user_id')
                user_data = get_member(user_id)
                edit_done = request.args.get('edit_done')
                err_msg = request.args.get('err_msg')
                note = request.args.get('note')
                return render_template(
                    'control_panel/members/edit_member.html',
                    dictionary=lang,
                    session=request.cookies,
                    user_id=user_id,
                    user_data=user_data,
                    edit_done=edit_done,
                    err_msg=err_msg,
                    note=note,
                )
            elif do == 'delete':
                return redirect(
                    url_for(
                        '.delete_member',
                        user_id=request.args.get('user_id')
                    )
                )
            elif do == 'activate':
                return redirect(
                    url_for(
                        '.activate_member',
                        user_id=request.args.get('user_id')
                    )
                )
            elif do == 'pending':
                users = get_all_members()
                deleted = request.args.get('deleted')
                activated = request.args.get('activated')
                return render_template(
                    'control_panel/members/members.html',
                    dictionary=lang,
                    session=request.cookies,
                    users=users,
                    deleted=deleted,
                    activated=activated,
                    pending=True,
                    user_id=user_id,
                )
            else:
                return redirect(url_for('.members'))
        else:
            return redirect('/admin')
    except Exception as e:
        print(e)
        return redirect('/admin')


@control_members.route('/admin/members/add_member', methods=['POST'])
def add_member():
    username = request.cookies.get('username')
    password = request.cookies.get('password')
    user_id = get_new_member_id()
    language = request.cookies.get('language')
    email = None
    lang = en
    try:
        if check_user(username, password):
            if language == 'ar':
                lang = ar
            else:
                lang = en
            # fetch the data from the request
            username = request.form.get('username')
            username = username.strip()
            password = request.form.get('password')
            password = password.strip()
            c_password = request.form.get('c_password')
            c_password = c_password.strip()
            email = request.form.get('email')
            full_name = request.form.get('fullname')
            group_id = request.form.get('group_id')
            reg_status = request.form.get('reg_status')
            # validate the inputs
            if group_id == 'on':
                group_id = 1
            else:
                group_id = 0
            if reg_status == 'on':
                reg_status = 1
            else:
                reg_status = 0
            if len(username) < 3 or username == '':
                raise Exception('invalid username')
            else:
                if len(password) < 8 or len(password) > 20:
                    raise Exception('invalid password')
                else:
                    if c_password != password:
                        raise Exception('invalid c_password')
                    else:
                        if len(full_name) < 7 or full_name.strip() == '':
                            raise Exception('invalid full name')
            # encode the password
            h = hashlib.md5(password.encode())
            password = h.hexdigest()
            # connect to the database and insert the user
            con = connect_to_db()
            rowcount = execute_dml_query(
                con,
                '''
                INSERT INTO users (
                    user_id,
                    username,
                    password,
                    email,
                    fullname,
                    group_id,
                    reg_status,
                    registration_date
                )
                VALUES (
                    {},
                    '{}',
                    '{}',
                    '{}',
                    '{}',
                    {},
                    {},
                    '{}'
                )
                '''.format(
                    user_id,
                    username,
                    password,
                    email,
                    full_name,
                    group_id,
                    reg_status,
                    '{} - {} - {}'.format(
                        datetime.datetime.now().day,
                        datetime.datetime.now().month,
                        datetime.datetime.now().year,
                    ),
                )
            )
            # close the connection
            if rowcount >= 1:
                return redirect(url_for('.members', do='add', add_done=True))
            else:
                return redirect(url_for('.members', do='add', add_done=False))
        else:
            return redirect('/admin')
    except Exception as e:
        print(e)
        e = str(e)
        if 'already exists' in e:
            if 'username' in e:
                return redirect(
                    url_for(
                        '.members',
                        do='add',
                        add_done=False,
                        err_msg='{} "{}" {}'.format(
                            lang['USERNAME'],
                            username,
                            lang['NOT_AVAILABLE']
                        )
                    )
                )
            elif 'email' in e:
                return redirect(
                    url_for(
                        '.members',
                        do='add',
                        add_done=False,
                        err_msg='{} "{}" {}'.format(
                            lang['EMAIL'],
                            email,
                            lang['NOT_AVAILABLE']
                        )
                    )
                )
        else:
            if e == 'invalid username':
                return redirect(
                    url_for(
                        '.members',
                        do='add',
                        add_done=False,
                        err_msg=lang['USERNAME_ERR_MSG'],
                        note=lang['USERNAME_NOTE']
                    )
                )
            elif e == 'invalid full name':
                return redirect(
                    url_for(
                        '.members',
                        do='add',
                        add_done=False,
                        err_msg=lang['FULL_NAME_ERR_MSG'],
                        note=lang['FULL_NAME_NOTE']
                    )
                )
            elif e == 'invalid password':
                return redirect(
                    url_for(
                        '.members',
                        do='add',
                        add_done=False,
                        err_msg=lang['PASSWORD_ERR_MSG'],
                        note=lang['PASSWORD_NOTE']
                    )
                )
            elif e == 'invalid c_password':
                return redirect(
                    url_for(
                        '.members',
                        do='add',
                        add_done=False,
                        err_msg=lang['C_PASSWORD_ERR_MSG']
                    )
                )
            # TODO: redirect to the 503 page
            return abort(503)


@control_members.route('/admin/members/edit_member', methods=['POST'])
def edit_member():
    current_username = request.cookies.get('username')
    current_password = request.cookies.get('password')
    language = request.cookies.get('language')
    username = None
    email = None
    user_id = None
    if check_user(current_username, current_password):
        try:
            # fetch the data from the request
            username = request.form.get('username')
            username = username.strip()
            old_username = request.form.get('old_username')
            password = request.form.get('password')
            password = password.strip()
            email = request.form.get('email')
            full_name = request.form.get('fullname')
            user_id = int(get_member_id(old_username))
            # validate the inputs
            if len(username) < 3 or username == '':
                raise Exception('invalid username')
            else:
                if password != '':
                    if len(password) < 8 or len(password) > 20:
                        raise Exception('invalid password')
                else:
                    if len(full_name) < 7 or full_name.strip() == '':
                        raise Exception('invalid full name')
            # encode the password
            h = hashlib.md5(password.encode())
            password = h.hexdigest()
            # connect to the database and update the user
            con = connect_to_db()
            if password != '':
                rowcount = execute_dml_query(
                    con,
                    '''
                    UPDATE
                        users
                    SET
                        username='{}',
                        password='{}',
                        email='{}',
                        fullname='{}'
                        WHERE
                            user_id={}
                    '''.format(
                        username,
                        password,
                        email,
                        full_name,
                        user_id,
                    ),
                )
            else:
                rowcount = execute_dml_query(
                    con,
                    '''
                    UPDATE
                        users
                    SET
                        username='{}',
                        email='{}',
                        fullname='{}'
                    WHERE
                        user_id={}
                    '''.format(
                        username,
                        email,
                        full_name,
                        user_id,
                    ),
                )
            # close the database connection
            if rowcount >= 1:
                return redirect(url_for('.members', do='edit', user_id=user_id, edit_done=True))
            else:
                return redirect(url_for('.members'))
        except Exception as e:
            e = str(e)
            if language == 'ar':
                lang = ar
            else:
                lang = en
            if 'already exists' in e:
                if 'username' in e:
                    return redirect(
                        url_for(
                            '.members',
                            do='edit',
                            user_id=user_id,
                            edit_done=False,
                            err_msg='{} "{}" {}'.format(
                                lang['USERNAME'],
                                username,
                                lang['NOT_AVAILABLE']
                            )
                        )
                    )
                elif 'email' in e:
                    return redirect(
                        url_for(
                            '.members',
                            do='edit',
                            user_id=user_id,
                            edit_done=False,
                            err_msg='{} "{}" {}'.format(
                                lang['EMAIL'],
                                email,
                                lang['NOT_AVAILABLE']
                            )
                        )
                    )
            else:
                if e == 'invalid username':
                    return redirect(
                        url_for(
                            '.members',
                            do='edit',
                            user_id=user_id,
                            edit_done=False,
                            err_msg=lang['USERNAME_ERR_MSG'],
                            note=lang['USERNAME_NOTE']
                        )
                    )
                elif e == 'invalid full name':
                    return redirect(
                        url_for(
                            '.members',
                            do='edit',
                            user_id=user_id,
                            edit_done=False,
                            err_msg=lang['FULL_NAME_ERR_MSG'],
                            note=lang['FULL_NAME_NOTE']
                        )
                    )
                elif e == 'invalid password':
                    return redirect(
                        url_for(
                            '.members',
                            do='edit',
                            user_id=user_id,
                            edit_done=False,
                            err_msg=lang['PASSWORD_ERR_MSG'],
                            note=lang['PASSWORD_NOTE']
                        )
                    )
                # TODO: redirect to the 503 page
                return abort(503)
    else:
        return redirect('/admin')


@control_members.route('/admin/members/delete/<user_id>')
def delete_member(user_id):
    try:
        username = request.cookies.get('username')
        password = request.cookies.get('password')
        if check_user(username, password):
            row = del_member(user_id)
            return redirect(url_for('.members', deleted=row))
        else:
            return redirect(url_for('index'))
    except Exception as e:
        print(e)
        return redirect(url_for('.members'))


@control_members.route('/admin/members/activate/<user_id>')
def activate_member(user_id):
    try:
        username = request.cookies.get('username')
        password = request.cookies.get('password')
        if check_user(username, password):
            row = ac_member(user_id)
            return redirect(url_for('.members', activated=row))
        else:
            return redirect('/admin')
    except Exception as e:
        print(e)
        return redirect(url_for('.members'))
