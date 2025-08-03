from flask import Blueprint, render_template, redirect,url_for
from flask_login import login_required, current_user
from app.models import IssueReport


main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/user/dashboard')
@login_required
def user_dashboard():
    return render_template('user_dashboard.html', name=current_user.username)

@main.route('/ngo/dashboard')
@login_required
def ngo_dashboard():
    if current_user.role != 'ngo':
        return redirect(url_for('main.user_dashboard'))

    issues = IssueReport.query.order_by(IssueReport.id.desc()).all()  # latest first
    return render_template('ngo_dashboard.html', issues=issues)