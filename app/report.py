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
        
        latitude = float(latitude) if latitude and latitude.strip() else None
        longitude = float(longitude) if longitude and longitude.strip() else None

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
    
    
    
@report_bp.route('/user/my_reports')
@login_required
def my_reports():
    if current_user.role != 'user':
        return redirect(url_for('main.ngo_dashboard'))

    reports = IssueReport.query.filter_by(user_id=current_user.id).order_by(IssueReport.timestamp.desc()).all()
    return render_template('my_reports.html', reports=reports)



@report_bp.route('/user/edit-report/<int:report_id>', methods=['GET', 'POST'])
@login_required
def edit_report(report_id):
    report = IssueReport.query.get_or_404(report_id)

    if report.user_id != current_user.id:
        flash("Unauthorized access to edit this report.", "danger")
        return redirect(url_for('report.my_reports'))

    if request.method == 'POST':
        # Handle Delete
        if 'delete' in request.form:
            db.session.delete(report)
            db.session.commit()
            flash('Report deleted successfully.', 'success')
            return redirect(url_for('report.my_reports'))
        
        report.title = request.form['title']
        report.description = request.form['description']
        report.location = request.form['location']
        report.latitude = request.form['latitude']
        report.longitude = request.form['longitude']

        db.session.commit()
        flash("Report updated successfully!", "success")
        return redirect(url_for('report.my_reports'))

    return render_template('edit_report.html', report=report)



@report_bp.route('/report/delete/<int:report_id>', methods=['GET'])
@login_required
def delete_report(report_id):
    report = IssueReport.query.get_or_404(report_id)
    if report.user_id != current_user.id:
        flash("You are not authorized to delete this report.", "danger")
        return redirect(url_for('report.view_reports'))

    db.session.delete(report)
    db.session.commit()
    flash("Report deleted successfully.", "success")
    return redirect(url_for('report.my_reports'))
