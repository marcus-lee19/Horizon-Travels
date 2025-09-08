from flask import Blueprint, render_template, session, redirect, url_for

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    if 'logged_in' in session and session.get('fname'):
        if session.get('usertype') == 'admin':
            # Redirect to admin dashboard if usertype is admin
            return redirect(url_for('admin.admin'))
        else:
            # Render the regular index page for standard users
            return render_template('index.html', name=session['fname'])
    else:
        # Render the index page for unauthenticated users
        return render_template('index.html', name=None)

#Student ID : 24017967
#Student Name : Marcus Lee
#Student Email : kun2.lee@live.uwe.ac.uk