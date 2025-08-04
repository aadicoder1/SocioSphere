from flask import Blueprint, render_template, redirect,url_for,flash,request
from flask_login import login_required, current_user
from app.models import IssueReport
from .extensions import db


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

    filter_status = request.args.get('status')
    if filter_status:
        issues = IssueReport.query.filter_by(status=filter_status).order_by(IssueReport.id.desc()).all()
    else:
        issues = IssueReport.query.order_by(IssueReport.id.desc()).all()
    return render_template('ngo_dashboard.html', issues=issues , filter_status=filter_status)


@main.route('/update_status/<int:issue_id>', methods=['POST'])
@login_required
def update_status(issue_id):
    if current_user.role != 'ngo':
        flash('Access denied.')
        return redirect(url_for('main.user_dashboard'))

    new_status = request.form['status']
    issue = IssueReport.query.get_or_404(issue_id)
    issue.status = new_status
    db.session.commit()
    flash('Status updated successfully.')
    return redirect(url_for('main.ngo_dashboard'))
