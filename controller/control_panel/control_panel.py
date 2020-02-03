import os
import hashlib
from flask import Blueprint, render_template, abort, redirect, url_for, request, session
from jinja2 import TemplateNotFound
from functions.languages.english import lang as en
from functions.languages.arabic import lang as ar
from functions.database.db import connect_to_db, execute_dql_query, execute_dml_query, get_user

control_panel = Blueprint('control_panel', __name__, template_folder='templates')

@control_panel.route('/admin')
def index():
    try:
        if session['username'] != '' and session['password'] != '':
            return redirect(url_for('.dashboard'))
        else:
            logging_in_failed = request.args.get('logging_in_failed')
            return render_template('control_panel/login.html', dictionary=en, logging_in_failed=logging_in_failed)
    except:
        try:
            logging_in_failed = request.args.get('logging_in_failed')
            return render_template('control_panel/login.html', dictionary=en, logging_in_failed=logging_in_failed)
        except:
            # TODO: redirect to the 404 page
            abort(404)

@control_panel.route('/admin/dashboard')
def dashboard():
    try:
        if session['username'] != '' and session['password'] != '':
            lang = None
            if session['language'] == 'ar':
                lang = ar
            else:
                lang = en
            return render_template('control_panel/dashboard.html', dictionary=lang, session=session)
        else:
            return redirect(url_for('.index'))
    except:
        try:
            return redirect(url_for('.index'))
        except:
            # TODO: redirect to the 404 page
            abort(404)

@control_panel.route('/admin/admin_login', methods=['POST',])
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

@control_panel.route('/admin/change_language')
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

@control_panel.route('/admin/logout')
def logout():
    try:
        session['username'] = ''
        session['password'] = ''
        session['fullname'] = ''
        return redirect(url_for('.index'))
    except:
        # TODO: redirect to the 404 page
        abort(404)

@control_panel.route('/admin/members')
def members():
    try:
        if session['username'] != '' and session['password'] != '':
            lang = None
            if session['language'] == 'ar':
                lang = ar
            else:
                lang = en
            do = request.args.get('do')
            if do == 'manage':
                pass
            elif do == 'edit':
                user_data = get_user(session['user_id'])
                edit_done = request.args.get('edit_done')
                err_msg   = request.args.get('err_msg')
                note      = request.args.get('note')
                return render_template('control_panel/edit_member.html', dictionary=lang, session=session, user_data=user_data, edit_done=edit_done, err_msg=err_msg, note=note)
        else:
            return redirect(url_for('.index'))
    except:
        try:
            return redirect(url_for('.index'))
        except:
            # TODO: redirect to the 404 page
            abort(404)

@control_panel.route('/admin/members/edit_member', methods=['POST',])
def edit_member():
    if request.method == 'POST':
        username  = ''
        password  = ''
        email     = ''
        full_name = ''
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
            # connect to the database and check the users
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
                        session['user_id'],
                    ),
                )
            else:
                rowcount = execute_dml_query(
                    con,
                    'UPDATE users SET username=\'{}\', email=\'{}\', fullname=\'{}\' WHERE user_id={}'.format(
                        username,
                        email,
                        full_name,
                        session['user_id'],
                    ),
                )
            # close the database connection
            con.close()
            if rowcount >= 1:
                return redirect(url_for('.members', do='edit', edit_done=True))
            else:
                return redirect(url_for('.members', do='edit', edit_done=False))
        except Exception as e:
            e = str(e)
            lang = ''
            if session['language'] == 'ar':
                lang = ar
            else:
                lang = en
            if 'already exists' in e:
                if 'username' in e:
                    return redirect(url_for('.members', do='edit', edit_done=False, err_msg='{} "{}" {}'.format(lang['USERNAME'], username, lang['NOT_AVALIABLE'])))
                elif 'email' in e:
                    return redirect(url_for('.members', do='edit', edit_done=False, err_msg='{} "{}" {}'.format(lang['EMAIL'], email, lang['NOT_AVALIABLE'])))
            else:
                if e == 'invalid username':
                    return redirect(url_for('.members', do='edit', edit_done=False, err_msg=lang['USERNAME_ERR_MSG'], note=lang['USERNAME_NOTE']))
                elif e == 'invalid full name':
                    return redirect(url_for('.members', do='edit', edit_done=False, err_msg=lang['FULL_NAME_ERR_MSG'], note=lang['FULL_NAME_NOTE']))
                elif e == 'invalid password':
                    return redirect(url_for('.members', do='edit', edit_done=False, err_msg=lang['PASSWORD_ERR_MSG'], note=lang['PASSWORD_NOTE']))
                # TODO: redirect to the 503 page
                return abort(503)
