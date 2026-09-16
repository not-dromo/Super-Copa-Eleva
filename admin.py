from flask import Blueprint, session, request, render_template, redirect, url_for, abort
from werkzeug.security import check_password_hash
from functools import wraps
import os
from models import db, PendingChange, Player
from datetime import datetime, timezone

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            return redirect(url_for('admin.admin_login'))
        return f(*args, **kwargs)
    return decorated_function

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

@admin_bp.route('/admin_dashboard')
@admin_required
def admin_dashboard():
    pending = PendingChange.query.filter_by(status='pending').all()
    return render_template('admin_dashboard.html', pendings=pending)

@admin_bp.route('/admin/pending/<int:pending_id>/approve', methods=['POST'])
@admin_required
def approve_pendency(pending_id):
    pending = PendingChange.query.get(pending_id)
    if pending is None or pending.status != 'pending':
        abort(404)

    setattr(pending.player, pending.field_name, pending.new_value)

    pending.status = 'approved'
    pending.reviewed_at = datetime.now(timezone.utc)

    db.session.commit()
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/admin/pending/<int:pending_id>/reject', methods=['POST'])
@admin_required
def reject_pendency(pending_id):
    pending = PendingChange.query.get(pending_id)
    if pending is None or pending.status != 'pending':
        abort(404)

    setattr(pending.player, pending.field_name, pending.new_value)

    pending.status = 'rejected'
    pending.admin_note = request.form.get('admin_note', '').strip()
    pending.reviewed_at = datetime.now(timezone.utc)

    db.session.commit()
    return redirect(url_for('admin.admin_dashboard'))
