from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from .models import IssueReport
from .extensions import db

report_bp = Blueprint('report', __name__, url_prefix='/user')

@report_bp.route('/report', methods=['GET', 'POST'])
@login_required
def report_issue():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']

        new_report = IssueReport(
            user_id=current_user.id,
            title=title,
            description=description
        )

        db.session.add(new_report)
        db.session.commit()

        flash('Issue reported successfully!','success')
        return redirect(url_for('main.user_dashboard'))  # or wherever

    return render_template('report_issue.html')
