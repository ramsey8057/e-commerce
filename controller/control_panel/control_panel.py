import os
import hashlib
from flask import Blueprint, render_template, abort, redirect, url_for, request
from jinja2 import TemplateNotFound
from functions.languages.english import lang as en
from functions.languages.arabic import lang as ar
from functions.database.db import connect_to_db, execute_query

control_panel_index_page = Blueprint('control_panel_index_page', __name__, template_folder='templates')

@control_panel_index_page.route('/')
def index():
    try:
        logged_in = request.args.get('logged_in')
        return render_template('control_panel/index.html', dictionary=en, logged_in=logged_in)
    except:
        abort(404)

@control_panel_index_page.route('/admin_login', methods=['POST',])
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
        row = execute_query(con, 'SELECT username, password FROM users WHERE username=\'{}\' AND password=\'{}\''.format(username, password))
        # close the database connection
        con.close()
        # check the username and password
        if row == []:
            return redirect(url_for('.index', logged_in=False))
        # redirect to the home page
        return redirect(url_for('.index', logged_in=True))
