from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from .models import IssueReport
from werkzeug.utils import secure_filename
from .extensions import db
import os

report_bp = Blueprint('report', __name__)

@report_bp.route('/user/report', methods=['GET', 'POST'])
@login_required
def report_issue():
    
    if current_user.role != 'user':
        return redirect(url_for('main.ngo_dashboard'))
    
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        
        image = request.files.get('image')
        image_filename = None
        if image and image.filename != '':
            filename = secure_filename(image.filename)
            image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            image_filename = filename
            
        location = request.form.get('location')
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')

        new_report = IssueReport(
            user_id=current_user.id,
            title=title,
            description=description,
            image_filename=image_filename,
            location=location,
            latitude=latitude,
            longitude=longitude
        )

        db.session.add(new_report)
        db.session.commit()

        flash('Issue reported successfully!','success')
        return redirect(url_for('main.user_dashboard'))  # or wherever

    return render_template('report_issue.html')



@report_bp.route('/view-reports')
@login_required
def view_reports():
    if current_user.role not in ['user', 'ngo']:
        flash("Unauthorized access", "danger")
        return redirect(url_for('main.index'))

    # Fetch reports with status "Pending" or "In Progress"
    notdone_reports = IssueReport.query.filter(IssueReport.status.in_(['Pending', 'In Progress'])).all()
    resolved_reports = IssueReport.query.filter_by(status='Resolved').all()
    
    return render_template('view_reports.html',
                           active_reports=notdone_reports, 
                           resolved_reports=resolved_reports)