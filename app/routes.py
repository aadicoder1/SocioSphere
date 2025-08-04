from flask import Blueprint, render_template, redirect,url_for,flash,request
from flask_login import login_required, current_user
from app.models import IssueReport
from .extensions import db
from flask_paginate import get_page_parameter



main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')


@main.route('/user/dashboard')
@login_required
def user_dashboard():
    return render_template('user_dashboard.html', name=current_user.username)


from flask_paginate import get_page_parameter

@main.route('/ngo/dashboard')
@login_required
def ngo_dashboard():
    if current_user.role != 'ngo':
        return redirect(url_for('main.user_dashboard'))

    # Get filter and pagination parameters
    filter_status = request.args.get('status')
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 5  # Number of issues per page

    # Build base query
    base_query = IssueReport.query
    if filter_status:
        base_query = base_query.filter_by(status=filter_status)

    # Apply pagination
    pagination = base_query.order_by(IssueReport.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    issues = pagination.items

    # Prepare issues with valid coordinates for map
    issues_json = [
        {
            "title": issue.title,
            "location": issue.location,
            "latitude": issue.latitude,
            "longitude": issue.longitude
        }
        for issue in issues
        if issue.latitude is not None and issue.longitude is not None
    ]

    return render_template(
        'ngo_dashboard.html',
        issues=issues,
        pagination=pagination,
        filter_status=filter_status,
        issues_json=issues_json
    )




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
