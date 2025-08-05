from flask import Blueprint, render_template, redirect,url_for,flash,request,current_app
from flask_login import login_required, current_user
from app.models import IssueReport, NGOEvent
from .extensions import db
from flask_paginate import get_page_parameter
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from flask_paginate import get_page_parameter



main = Blueprint('main', __name__)




@main.route('/')
def index():
    return render_template('index.html')




@main.route('/user/dashboard')
@login_required
def user_dashboard():
    if current_user.role != 'user':
        return redirect(url_for('main.ngo_dashboard'))

    from app.models import NGOEvent  
    # Get all events, latest first
    events = NGOEvent.query.order_by(NGOEvent.date.desc()).all()
    return render_template('user_dashboard.html', name=current_user.username, events=events)





@main.route('/ngo/dashboard')
@login_required
def ngo_dashboard():
    if current_user.role != 'ngo':
        return redirect(url_for('main.user_dashboard'))

    # Get filter and pagination parameters
    filter_status = request.args.get('status')
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 5  # Number of issues per page

    base_query = IssueReport.query
    if filter_status:
        base_query = base_query.filter_by(status=filter_status)

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
        name=current_user.username,
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




@main.route('/events')
@login_required
def ngo_events():
    
    events = NGOEvent.query.order_by(NGOEvent.date.desc()).all()
    return render_template('ngo_events.html', events=events)




@main.route('/ngo/events/create', methods=['GET', 'POST'])
@login_required
def create_event():
    if current_user.role != 'ngo':
        return redirect(url_for('main.user_dashboard'))

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form['description']
        date = request.form['date']
        location = request.form['location']
        image = request.files.get('image')
        
        if not title or not description or not date or not location:
            flash("All fields except image are required.", "danger")
            return redirect(request.url)
        
        try:
            event_date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', 'danger')
            return redirect(request.url)

        image_filename = None
        if image:
            image_filename = secure_filename(image.filename)
            image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], image_filename))

        event = NGOEvent(
            title=title,
            description=description,
            date=event_date,
            location=location,
            image_filename=image_filename,
            created_by=current_user.id
        )
        db.session.add(event)
        db.session.commit()

        flash('Event created successfully!', 'success')
        return redirect(url_for('main.ngo_events'))

    return render_template('create_event.html')




@main.route('/events')
@login_required
def view_events():
    if current_user.role != 'user':
        #flash('Access denied: Only users can view this page.', 'danger')
        return redirect(url_for('main.ngo_events'))
    
    events = NGOEvent.query.order_by(NGOEvent.date).all()
    return render_template('view_events.html', events=events)



#edits event
from datetime import datetime

@main.route('/ngo/event/<int:event_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_event(event_id):
    event = NGOEvent.query.get_or_404(event_id)

    if current_user.id != event.created_by:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('main.ngo_dashboard'))

    if request.method == 'POST':
        event.title = request.form['title']
        event.description = request.form['description']
        event.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        event.location = request.form['location']

        # Image upload (optional)
        if 'image' in request.files:
            image = request.files['image']
            if image.filename:
                filename = secure_filename(image.filename)
                image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                event.image_filename = filename

        db.session.commit()
        flash('Event updated successfully.', 'success')
        return redirect(url_for('main.ngo_events'))

    return render_template('edit_event.html', event=event)



# Delete event
@main.route('/ngo/event/<int:event_id>/delete')
@login_required
def delete_event(event_id):
    event = NGOEvent.query.get_or_404(event_id)

    if current_user.id != event.created_by:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('main.ngo_dashboard'))

    db.session.delete(event)
    db.session.commit()
    flash('Event deleted successfully.', 'success')
    return redirect(url_for('main.ngo_events'))