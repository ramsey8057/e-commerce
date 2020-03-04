import datetime
import hashlib
from flask import Blueprint, render_template, url_for, request, redirect, make_response
from functions.languages.arabic import lang as ar
from functions.languages.english import lang as en
from functions.database.db import connect_to_db, execute_dml_query
from functions.members.members import check_user, check_user_for_log_in
from functions.database.members_db.db import get_members_count, get_pending_members_count,\
                                            get_latest_registered_members, get_member_id, get_member_fullname
from functions.database.items_db.db import get_items_count, get_latest_items
from functions.database.comments_db.db import get_comments_count

control_panel = Blueprint('control_panel', __name__, template_folder='templates')


@control_panel.route('/admin')
def index():
    try:
        username = request.cookies.get('username')
        password = request.cookies.get('password')
        language = request.cookies.get('language')
        if language == 'ar':
            lang = ar
        else:
            lang = en
        if all([username is not None, password is not None]):
            if check_user(username, password):
                return redirect(url_for('.dashboard'))
            else:
                logging_in_failed = request.args.get('logging_in_failed')
                return render_template('control_panel/login.html', logging_in_failed=logging_in_failed)
        else:
            logging_in_failed = request.args.get('logging_in_failed')
            return render_template(
                'control_panel/login.html',
                dictionary=lang,
                logging_in_failed=logging_in_failed
            )
    except Exception as e:
        print(e)
        logging_in_failed = request.args.get('logging_in_failed')
        print('4')
        return render_template(
            'control_panel/login.html',
            dictionary=en,
            logging_in_failed=logging_in_failed
        )


@control_panel.route('/admin/admin_login', methods=['POST'])
def login():
    # fetch data from the request
    username = request.form.get('username')
    password = request.form.get('password')
    # encode the password
    h = hashlib.md5(password.encode())
    password = h.hexdigest()
    # connect to the database and check the users
    if check_user_for_log_in(username, password):
        response = make_response(redirect(url_for('.dashboard')))
        expire_date = datetime.datetime.now()
        expire_date = expire_date + datetime.timedelta(days=400)
        response.set_cookie('username', username, expires=expire_date)
        response.set_cookie('password', password, expires=expire_date)
        response.set_cookie('fullname', get_member_fullname(username), expires=expire_date)
        response.set_cookie('user_id', get_member_id(username), expires=expire_date)
        response.set_cookie('language', 'en', expires=expire_date)
        return response
    else:
        return redirect(url_for('.index', logging_in_failed=True))


@control_panel.route('/admin/logout')
def logout():
    try:
        user_id = request.cookies.get('user_id')
        # connect to db
        con = connect_to_db()
        # set the is logged in column to 0
        execute_dml_query(
            con,
            '''
            UPDATE
                users
            SET
                is_logged_in=0
            WHERE
                user_id={}
            '''.format(
                int(user_id)
            )
        )
        # close the database connection
        response = make_response(redirect(url_for('.index')))
        response.set_cookie('username', max_age=0)
        response.set_cookie('password', max_age=0)
        response.set_cookie('fullname', max_age=0)
        response.set_cookie('user_id', max_age=0)
        response.set_cookie('language', max_age=0)
        return response
    except Exception as e:
        print(e)
        return redirect(url_for('.index'))


@control_panel.route('/admin/dashboard')
def dashboard():
    username = request.cookies.get('username')
    password = request.cookies.get('password')
    language = request.cookies.get('language')
    if language == 'ar':
        lang = ar
    else:
        lang = en
    if check_user(username, password):
        users_count = get_members_count()
        pending_users_count = get_pending_members_count()
        latest_users = get_latest_registered_members()
        user_id = get_member_id(request.cookies.get('username'))
        items_count = get_items_count()
        latest_items = get_latest_items()
        comments_count = get_comments_count()
        return render_template(
            'control_panel/dashboard.html',
            dictionary=lang,
            session=request.cookies,
            users_count=users_count,
            pending_users_count=pending_users_count,
            latest_users=latest_users,
            user_id=user_id,
            items_count=items_count,
            latest_items=latest_items,
            comments_count=comments_count
        )
    else:
        return redirect(url_for('.index'))


@control_panel.route('/admin/change_language')
def change_language():
    username = request.cookies.get('username')
    password = request.cookies.get('password')
    if check_user(username, password):
        language = request.cookies.get('language')
        response = make_response(redirect(url_for('.index')))
        expire_date = datetime.datetime.now()
        expire_date = expire_date + datetime.timedelta(days=400)
        if language == 'en':
            response.set_cookie('language', 'ar', expires=expire_date)
        else:
            response.set_cookie('language', 'en', expires=expire_date)
        return response
    else:
        return redirect(url_for('.index'))
