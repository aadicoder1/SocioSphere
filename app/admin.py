from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models import User, NGOEvent, IssueReport, Post,Contribution  # adjust according to your structure
from .extensions import db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('main.index'))  # restrict access

    users = User.query.all()
    ngos = NGOEvent.query.all()
    reports = IssueReport.query.all()
    events = NGOEvent.query.all()

    return render_template('admin/dashboard.html', users=users, ngos=ngos, reports=reports, events=events)
