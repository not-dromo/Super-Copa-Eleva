from flask import Blueprint, session, request, render_template, redirect, url_for
from werkzeug.security import check_password_hash
import os

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password', '')
        saved_hash = os.environ.get('ADMIN_PASSWORD_HASH')

        if check_password_hash(saved_hash, password):
            session['is_admin'] = True
            return redirect(url_for('admin.admin_dashboard'))
        else:
            return render_template('admin_login.html', error='invalid login')

    return render_template('admin_login.html')
