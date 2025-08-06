from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.models import IssueReport, NGOEvent
from .extensions import db
from flask_paginate import get_page_parameter
import os
from werkzeug.utils import secure_filename
from datetime import datetime, date

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/user/dashboard')
@login_required
def user_dashboard():
    if current_user.role != 'user':
        return redirect(url_for('main.ngo_dashboard'))

    events = NGOEvent.query.order_by(NGOEvent.date.desc()).all()
    return render_template('user_dashboard.html', name=current_user.username, events=events)

@main.route('/ngo/dashboard')
@login_required
def ngo_dashboard():
    if current_user.role != 'ngo':
        return redirect(url_for('main.user_dashboard'))

    filter_status = request.args.get('status')
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = 5

    base_query = IssueReport.query
    if filter_status:
        base_query = base_query.filter_by(status=filter_status)

    pagination = base_query.order_by(IssueReport.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    issues = pagination.items

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

    if new_status.lower() == 'resolved':
        issue.resolved_by_id = current_user.id
    else:
        issue.resolved_by_id = None

    db.session.commit()
    flash('Status updated successfully.')
    return redirect(url_for('main.ngo_dashboard'))

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

@main.route('/ngo/events')
@login_required
def ngo_events():
    if current_user.role != 'ngo':
        return redirect(url_for('main.user_dashboard'))

    events = NGOEvent.query.filter_by(created_by=current_user.id).order_by(NGOEvent.date.desc()).all()
    return render_template('ngo_events.html', events=events)

@main.route('/events')
@login_required
def view_events():
    if current_user.role != 'user':
        return redirect(url_for('main.ngo_events'))

    today = date.today()
    past_events = NGOEvent.query.filter(NGOEvent.date < today).all()
    for e in past_events:
        db.session.delete(e)
    db.session.commit()

    search = request.args.get('search', '')
    start_date = request.args.get('start_date', '')
    end_date = request.args.get('end_date', '')
    sort_order = request.args.get('sort', 'asc')

    query = NGOEvent.query

    if search:
        query = query.filter(
            NGOEvent.title.ilike(f"%{search}%") |
            NGOEvent.location.ilike(f"%{search}%")
        )
    if start_date:
        query = query.filter(NGOEvent.date >= start_date)
    if end_date:
        query = query.filter(NGOEvent.date <= end_date)

    if sort_order == 'desc':
        query = query.order_by(NGOEvent.date.desc())
    else:
        query = query.order_by(NGOEvent.date.asc())

    events = query.all()
    return render_template('view_events.html', events=events, search=search, start_date=start_date, end_date=end_date, sort_order=sort_order)

@main.route('/events/<int:event_id>')
@login_required
def event_detail(event_id):
    event = NGOEvent.query.get_or_404(event_id)
    return render_template('event_detail.html', event=event)

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
        event.sponsors = request.form.get('sponsors')

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