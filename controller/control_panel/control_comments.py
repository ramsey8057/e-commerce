from flask import Blueprint, render_template, redirect, url_for, request
from functions.languages.arabic import lang as ar
from functions.languages.english import lang as en
from functions.database.db import connect_to_db, execute_dml_query
from functions.database.comments_db.db import get_all_comments, del_comment, get_comment
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
                all_comments = get_all_comments()
                deleted = request.args.get('deleted')
                return render_template(
                    'control_panel/comments/comments.html',
                    dictionary=lang,
                    session=request.cookies,
                    comments=all_comments,
                    deleted=deleted,
                    user_id=user_id
                )
            elif do == 'edit':
                comment_id = request.args.get('comment_id')
                comment_data = get_comment(comment_id)
                edit_done = request.args.get('edit_done')
                err_msg = request.args.get('err_msg')
                note = request.args.get('note')
                return render_template(
                    'control_panel/comments/edit_comment.html',
                    dictionary=lang,
                    session=request.cookies,
                    comment_data=comment_data[0],
                    edit_done=edit_done,
                    err_msg=err_msg,
                    note=note,
                    comment_id=comment_id,
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


@control_comments.route('/admin/comments/edit_comment', methods=['POST'])
def edit_comment():
    current_username = request.cookies.get('username')
    current_password = request.cookies.get('password')
    try:
        if check_user(current_username, current_password):
            # fetch the data from the request
            comment_id = request.form.get('id')
            comment = request.form.get('comment')
            # connect to the database and insert the category
            con = connect_to_db()
            rowcount = execute_dml_query(
                con,
                '''
                UPDATE
                    comments
                SET comment = '{}'
                WHERE comment_id = {}
                '''.format(
                    comment,
                    comment_id
                )
            )
            # close the database connection
            if rowcount >= 1:
                return redirect(
                    url_for(
                        '.comments',
                        do='edit',
                        edit_done=True,
                        comment_id=comment_id
                    )
                )
            else:
                return redirect(
                    url_for(
                        '.comments',
                        do='edit',
                        edit_done=False,
                        comment_id=comment_id
                    )
                )
        else:
            return redirect('/admin')
    except Exception as e:
        print(e)
        return redirect(url_for('.comments'))
