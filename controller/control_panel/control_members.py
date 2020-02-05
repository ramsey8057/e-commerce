import hashlib
import datetime
from flask import Blueprint, render_template, abort, redirect, url_for, request, session
from functions.languages.english import lang as en
from functions.languages.arabic import lang as ar
from functions.database.members_db.db import *
from functions.database.db import *

control_members = Blueprint('control_members', __name__, template_folder='templates')

@control_members.route('/admin')
def index():
    try:
        if session['username'] != '' and session['password'] != '':
            return redirect(url_for('.dashboard'))
        else:
            logging_in_failed = request.args.get('logging_in_failed')
            return render_template('control_panel/members/login.html', dictionary=en, logging_in_failed=logging_in_failed)
    except:
        try:
            logging_in_failed = request.args.get('logging_in_failed')
            return render_template('control_panel/members/login.html', dictionary=en, logging_in_failed=logging_in_failed)
        except:
            # TODO: redirect to the 404 page
            abort(404)

@control_members.route('/admin/dashboard')
def dashboard():
    try:
        if session['username'] != '' and session['password'] != '':
            lang = None
            if session['language'] == 'ar':
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
    except:
        try:
            return redirect(url_for('.index'))
        except:
            # TODO: redirect to the 404 page
            abort(404)

@control_members.route('/admin/admin_login', methods=['POST', ])
def login():
    if request.method == 'POST':
        # fetch the data from the request
        username = request.form['username']
        password = request.form['password']
        # encode the password
        h = hashlib.md5(password.encode())
        password = h.hexdigest()
        # connect to the database and check the users
        con = connect_to_db()
        row = execute_dql_query(
            con,
            'SELECT user_id, username, password, fullname FROM users WHERE username=\'{}\' AND password=\'{}\' AND group_id=1 AND reg_status=1'.format(
                username,
                password
            )
        )
        # close the database connection
        con.close()
        # check the username and password
        if row == []:
            return redirect(url_for('.index', logging_in_failed=True))
        # redirect to the home page
        session['username'] = username
        session['password'] = password
        session['fullname'] = row[0][3]
        session['user_id']  = row[0][0]
        try:
            if session['language'] == None:
                session['language'] = 'en'
        except:
            session['language'] = 'en'
        return redirect(url_for('.index'))
    else:
        return redirect('/admin')

@control_members.route('/admin/change_language')
def change_language():
    try:
        if session['language'] == 'en':
            session['language'] = 'ar'
        else:
            session['language'] = 'en'
        return redirect(url_for('.index'))
    except:
        # TODO: redirect to the 404 page
        abort(404)

@control_members.route('/admin/logout')
def logout():
    try:
        session['username'] = ''
        session['password'] = ''
        session['fullname'] = ''
        return redirect(url_for('.index'))
    except:
        # TODO: redirect to the 404 page
        abort(404)

@control_members.route('/admin/members')
def members():
    try:
        if session['username'] != '' and session['password'] != '':
            lang = None
            if session['language'] == 'ar':
                lang = ar
            else:
                lang = en
            do = request.args.get('do')
            if do == None:
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
                err_msg   = request.args.get('err_msg')
                note      = request.args.get('note')
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
                err_msg   = request.args.get('err_msg')
                note      = request.args.get('note')
                return render_template('control_panel/members/add_member.html', dictionary=lang, add_done=add_done, err_msg=err_msg, note=note)
            elif do == 'delete':
                return redirect(url_for('.delete_member', user_id=request.args['user_id']))
            elif do == 'activate':
                return redirect(url_for('.activate_member',user_id=request.args['user_id']))
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
                user_id = request.args['user_id']
                return redirect(url_for('.members'))
        else:
            return redirect(url_for('.index'))
    except Exception as e:
        print(e)
        try:
            return redirect(url_for('.index'))
        except:
            # TODO: redirect to the 404 page
            abort(404)

@control_members.route('/admin/members/edit_member', methods=['POST', ])
def edit_member():
    if request.method == 'POST':
        user_id = request.form['user_id']
        username  = None
        password  = None
        email     = None
        full_name = None
        try:
            # fetch the data from the request
            username  = request.form['username']
            username  = username.strip()
            password  = request.form['password']
            password  = password.strip()
            email     = request.form['email']
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
            rowcount = 0
            if password != '':
                rowcount = execute_dml_query(
                    con,
                    'UPDATE users SET username=\'{}\', password=\'{}\', email=\'{}\', fullname=\'{}\' WHERE user_id={}'.format(
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
                    'UPDATE users SET username=\'{}\', email=\'{}\', fullname=\'{}\' WHERE user_id={}'.format(
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
            lang = None
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

@control_members.route('/admin/members/add_member', methods=['POST',])
def add_member():
    if request.method == 'POST':
        user_id    = get_new_member_id()
        username   = None
        password   = None
        cpassword  = None
        email      = None
        full_name  = None
        group_id   = None
        reg_status = None
        try:
            # fetch the data from the request
            username   = request.form['username']
            username   = username.strip()
            password   = request.form['password']
            password   = password.strip()
            cpassword  = request.form['cpassword']
            cpassword  = cpassword.strip()
            email      = request.form['email']
            full_name  = request.form['fullname']
            group_id   = request.form.get('group_id')
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
            h         = hashlib.md5(password.encode())
            password  = h.hexdigest()
            h         = hashlib.md5(cpassword.encode())
            cpassword = h.hexdigest()
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
            lang = None
            if session['language'] == 'ar':
                lang = ar
            else:
                lang = en
            if 'already exists' in e:
                if 'username' in e:
                    return redirect(url_for('.members', do='add', add_done=False,
                                            err_msg='{} "{}" {}'.format(lang['USERNAME'], username,
                                                                        lang['NOT_AVAILABLE'])))
                elif 'email' in e:
                    return redirect(url_for('.members', do='add', add_done=False,
                                            err_msg='{} "{}" {}'.format(lang['EMAIL'], email,
                                                                        lang['NOT_AVAILABLE'])))
            else:
                if e == 'invalid username':
                    return redirect(url_for('.members', do='add', add_done=False, err_msg=lang['USERNAME_ERR_MSG'], note=lang['USERNAME_NOTE']))
                elif e == 'invalid full name':
                    return redirect(url_for('.members', do='add', add_done=False, err_msg=lang['FULL_NAME_ERR_MSG'],
                                            note=lang['FULL_NAME_NOTE']))
                elif e == 'invalid password':
                    return redirect(url_for('.members', do='add', add_done=False, err_msg=lang['PASSWORD_ERR_MSG'],
                                            note=lang['PASSWORD_NOTE']))
                elif e == 'invalid cpassword':
                    return redirect(url_for('.members', do='add', add_done=False, err_msg=lang['CPASSWORD_ERR_MSG']))
                # TODO: redirect to the 503 page
                return abort(503)
    else:
        return redirect('/admin')

@control_members.route('/admin/members/delete/<user_id>')
def delete_member(user_id):
    try:
        row = del_member(user_id)
        return redirect(url_for('.members', deleted=row))
    except:
        try:
            return redirect(url_for('.members'))
        except:
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
    except:
        try:
            return redirect(url_for('.members'))
        except:
            # TODO: redirect to the 404 page
            return abort(404)
