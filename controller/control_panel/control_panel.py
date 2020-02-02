import os
import hashlib
from flask import Blueprint, render_template, abort, redirect, url_for, request, session
from jinja2 import TemplateNotFound
from functions.languages.english import lang as en
from functions.languages.arabic import lang as ar
from functions.database.db import connect_to_db, execute_query

control_panel_index_page = Blueprint('control_panel_index_page', __name__, template_folder='templates')

@control_panel_index_page.route('/admin')
def index():
    try:
        if session['username'] != '' and session['password'] != '':
            return redirect(url_for('.dashboard'))
        else:
            logging_in_failed = request.args.get('logging_in_failed')
            return render_template('control_panel/login.html', dictionary=ar, logging_in_failed=logging_in_failed)
    except:
        try:
            logging_in_failed = request.args.get('logging_in_failed')
            return render_template('control_panel/login.html', dictionary=en, logging_in_failed=logging_in_failed)
        except:
            abort(404)

@control_panel_index_page.route('/admin/dashboard')
def dashboard():
    try:
        if session['username'] != '' and session['password'] != '':
            if session['language'] == 'ar':
                return render_template('control_panel/dashboard.html', dictionary=ar, session=session)
            else:
                return render_template('control_panel/dashboard.html', dictionary=en, session=session)
        else:
            return redirect(url_for('.index'))
    except:
        try:
            return redirect(url_for('.index'))
        except:
            abort(404)

@control_panel_index_page.route('/admin/admin_login', methods=['POST',])
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
        row = execute_query(
            con,
            'SELECT username, password, fullname FROM users WHERE username=\'{}\' AND password=\'{}\' AND group_id=1 AND reg_status=1'.format(
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
        session['fullname'] = row[0][2]
        try:
            if session['language'] == None:
                session['language'] = 'en'
        except:
            session['language'] = 'en'
        return redirect(url_for('.index'))

@control_panel_index_page.route('/admin/change_language')
def change_language():
    try:
        if session['language'] == 'en':
            session['language'] = 'ar'
        else:
            session['language'] = 'en'
        return redirect(url_for('.index'))
    except:
        abort(404)

@control_panel_index_page.route('/admin/logout')
def logout():
    try:
        session['username'] = ''
        session['password'] = ''
        session['fullname'] = ''
        return redirect(url_for('.index'))
    except:
        abort(404)
