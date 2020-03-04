from flask import Blueprint, render_template, abort, redirect, url_for, request
from functions.languages.arabic import lang as ar
from functions.languages.english import lang as en
from functions.database.comments_db.db import get_all_comments, del_comment
from functions.database.members_db.db import get_member_id
from functions.members.members import check_user

control_comments = Blueprint('control_comments', __name__, template_folder='templates')


@control_comments.route('/admin/comments')
def comments():
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
                comments = get_all_comments()
                deleted = request.args.get('deleted')
                return render_template(
                    'control_panel/comments/comments.html',
                    dictionary=lang,
                    session=request.cookies,
                    comments=comments,
                    deleted=deleted,
                    user_id=user_id
                )
            elif do == 'delete':
                return redirect(
                    url_for(
                        '.delete_comment',
                        comment_id=request.args.get('comment_id')
                    ),
                )
            else:
                return redirect(url_for('.items'))
        else:
            return redirect('/admin')
    except Exception as e:
        print(e)
        return redirect('/admin')


@control_comments.route('/admin/comments/delete/<comment_id>')
def delete_comment(comment_id):
    try:
        username = request.cookies.get('username')
        password = request.cookies.get('password')
        if check_user(username, password):
            row = del_comment(comment_id)
            return redirect(url_for('.comments', deleted=row))
        else:
            return redirect(url_for('index'))
    except Exception as e:
        print(e)
        return redirect(url_for('.comments'))
