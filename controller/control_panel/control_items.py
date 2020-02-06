import datetime
from flask import Blueprint, Flask, render_template, abort, redirect, url_for, request, session
from functions.languages.arabic import lang as ar
from functions.languages.english import lang as en
from functions.database.db import *
from functions.database.items_db.db import *

control_items = Blueprint('control_items', __name__, template_folder='templates')

@control_items.route('/admin/items')
def items():
    try:
        if session['username'] != '' and session['password'] != '':
            lang = None
            if session['language'] == 'ar':
                lang = ar
            else:
                lang = en
            do = request.args.get('do')
            if do == None:
                return 'Welcome to items page'
            elif do == 'edit':
                pass
            elif do == 'add':
                add_done = request.args.get('add_done')
                err_msg = request.args.get('err_msg')
                return render_template(
                    'control_panel/items/add_item.html',
                    dictionary=lang,
                    session=session,
                    add_done=add_done,
                    err_msg=err_msg,
                )
            elif do == 'delete':
                pass
            elif do == 'approve':
                pass
            else:
                return redirect(url_for('.items'))
    except:
        try:
            return redirect('/admin')
        except:
            # TODO: redirect to the 404 page
            abort(404)
