import hashlib
import datetime
from flask import Blueprint, render_template, abort, redirect, url_for, request, session
from functions.languages.english import lang as en
from functions.languages.arabic import lang as ar
from functions.database.members_db.db import *
from functions.members.members import *

control_members = Blueprint('control_members', __name__, template_folder='templates')


@control_members.route('/admin')
def index():
    try:
        username = request.cookies.get('ramsey-e-commerce-username')
        password = request.cookies.get('ramsey-e-commerce-password')
        print(username)
        print(password)
        if username is None or password is None:
            logging_in_failed = request.args.get('logging_in_failed')
            return render_template(
                'control_panel/members/login.html',
                dictionary=en,
                logging_in_failed=logging_in_failed
            )
        else:
            lang = request.cookies.get('language')
            if lang is None or lang == '':
                lang = 'en'
            if check_user(username, password, lang):
                return redirect(url_for('.dashboard'))
            else:
                return render_template(
                    'control_panel/members/login.html',
                    dictionary=en,
                    logging_in_failed=True
                )
    except Exception as e:
        print(e)
        try:
            logging_in_failed = request.args.get('logging_in_failed')
            return render_template(
                'control_panel/members/login.html',
                dictionary=en,
                logging_in_failed=logging_in_failed
            )
        except Exception as e:
            print(e)
            # TODO: redirect to the 404 page
            return abort(404)


@control_members.route('/admin/dashboard')
def dashboard():
    try:
        username = request.cookies.get('username')
        password = request.cookies.get('password')
        language = request.cookies.get('language')
        if check_user(username, password, language):
            if language == 'ar':
                lang = ar
            else:
                lang = en
            users_count = get_members_count()
            pending_users_count = get_pending_members_count()
            latest_users = get_latest_registerd_members()
            return render_template(
                'control_panel/dashboard.html',
                dictionary=lang,
                session=session,
                users_count=users_count,
                pending_users_count=pending_users_count,
                latest_users=latest_users
            )
        else:
            return redirect(url_for('.index'))
    except Exception as e:
        print(e)
        try:
            return redirect(url_for('.index'))
        except Exception as e:
            print(e)
            # TODO: redirect to the 404 page
            return abort(404)


@control_members.route('/admin/admin_login', methods=['POST'])
def login():
    if request.method == 'POST':
        # fetch data from the request
        username = request.form.get('username')
        password = request.form.get('password')
        # encode the password
        h = hashlib.md5(password.encode())
        password = h.hexdigest()
        # check user
        if check_user(username, password, 'en'):
            return redirect(url_for('.index'))
        else:
            return redirect(url_for('.index', logging_in_failed=True))
    else:
        return redirect('.index')


@control_members.route('/admin/change_language')
def change_language():
    try:
        response = make_response('new response')
        if request.cookies.get('language') == 'ar':
            response.set_cookie('language', 'ar')
        else:
            response.set_cookie('language', 'en')
    except Exception as e:
        print(e)
        # TODO: redirect to the 404 page
        return abort(404)


@control_members.route('/admin/logout')
def logout():
    try:
        username = request.cookies.get('username')
        logout_from_all(username)
        return redirect(url_for('.index'))
    except Exception as e:
        print(e)
        # TODO: redirect to the 404 page
        return abort(404)


@control_members.route('/admin/members')
def members():
    try:
        if session['username'] != '' and session['password'] != '':
            if session['language'] == 'ar':
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
                    session=session,
                    users=users,
                    deleted=deleted,
                    activated=activated,
                    pending=False
                )
            elif do == 'edit':
                user_id = request.args['user_id']
                user_data = get_member(user_id)
                edit_done = request.args.get('edit_done')
                err_msg = request.args.get('err_msg')
                note = request.args.get('note')
                return render_template(
                    'control_panel/members/edit_member.html',
                    dictionary=lang,
                    session=session,
                    user_id=user_id,
                    user_data=user_data,
                    edit_done=edit_done,
                    err_msg=err_msg,
                    note=note
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
                    note=note
                )
            elif do == 'delete':
                return redirect(
                    url_for(
                        '.delete_member',
                        user_id=request.args['user_id']
                    )
                )
            elif do == 'activate':
                return redirect(
                    url_for(
                        '.activate_member',
                        user_id=request.args['user_id']
                    )
                )
            elif do == 'pending':
                users = get_all_members()
                deleted = request.args.get('deleted')
                activated = request.args.get('activated')
                return render_template(
                    'control_panel/members/members.html',
                    dictionary=lang,
                    session=session,
                    users=users,
                    deleted=deleted,
                    activated=activated,
                    pending=True
                )
            else:
                return redirect(url_for('.members'))
        else:
            return redirect(url_for('.index'))
    except Exception as e:
        print(e)
        try:
            return redirect(url_for('.index'))
        except Exception as e:
            print(e)
            # TODO: redirect to the 404 page
            abort(404)


@control_members.route('/admin/members/edit_member', methods=['POST'])
def edit_member():
    if request.method == 'POST':
        user_id = request.form['user_id']
        username = None
        email = None
        try:
            # fetch the data from the request
            username = request.form['username']
            username = username.strip()
            password = request.form['password']
            password = password.strip()
            email = request.form['email']
            full_name = request.form['fullname']
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
            con.close()
            if rowcount >= 1:
                return redirect(url_for('.members', do='edit', user_id=user_id, edit_done=True))
            else:
                return redirect(url_for('.members'))
        except Exception as e:
            e = str(e)
            if session['language'] == 'ar':
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


@control_members.route('/admin/members/add_member', methods=['POST'])
def add_member():
    if request.method == 'POST':
        user_id = get_new_member_id()
        username = None
        email = None
        try:
            # fetch the data from the request
            username = request.form['username']
            username = username.strip()
            password = request.form['password']
            password = password.strip()
            cpassword = request.form['cpassword']
            cpassword = cpassword.strip()
            email = request.form['email']
            full_name = request.form['fullname']
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
                    if cpassword != password:
                        raise Exception('invalid cpassword')
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
            con.close()
            if rowcount >= 1:
                return redirect(url_for('.members', do='add', add_done=True))
            else:
                return redirect(url_for('.members', do='add', add_done=False))
        except Exception as e:
            e = str(e)
            if session['language'] == 'ar':
                lang = ar
            else:
                lang = en
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
                elif e == 'invalid cpassword':
                    return redirect(
                        url_for(
                            '.members',
                            do='add',
                            add_done=False,
                            err_msg=lang['CPASSWORD_ERR_MSG']
                        )
                    )
                # TODO: redirect to the 503 page
                return abort(503)
    else:
        return redirect('/admin')


@control_members.route('/admin/members/delete/<user_id>')
def delete_member(user_id):
    try:
        row = del_member(user_id)
        return redirect(url_for('.members', deleted=row))
    except Exception as e:
        print(e)
        try:
            return redirect(url_for('.members'))
        except Exception as e:
            print(e)
            # TODO: redirect to the 404 page
            return abort(404)


@control_members.route('/admin/members/activate/<user_id>')
def activate_member(user_id):
    try:
        if session['username'] != '' and session['password'] != '':
            row = ac_member(user_id)
            return redirect(url_for('.members', activated=row))
        else:
            return redirect('/admin')
    except Exception as e:
        print(e)
        try:
            return redirect(url_for('.members'))
        except Exception as e:
            print(e)
            # TODO: redirect to the 404 page
            return abort(404)
