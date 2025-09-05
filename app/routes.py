from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.models import IssueReport, NGOEvent, User, Contribution ,Post
from .extensions import db
from flask_paginate import get_page_parameter
import os
from app.forms import PostForm 
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
    elif current_user.role == 'admin':
        return redirect(url_for('admin.dashboard'))

    # Fetch latest events
    events = NGOEvent.query.order_by(NGOEvent.date.desc()).all()

    # Fetch latest posts
    posts = Post.query.order_by(Post.timestamp.desc()).all()

    return render_template(
        'user_dashboard.html',
        name=current_user.username,
        events=events,
        posts=posts
    )


@main.route('/ngo/dashboard')
@login_required
def ngo_dashboard():
    if current_user.role != 'ngo':
        return redirect(url_for('main.user_dashboard'))
    elif current_user.role == 'admin':
        return redirect(url_for('admin.dashboard'))

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
        flash('Access denied.', 'danger')
        return redirect(url_for('main.user_dashboard'))
    elif current_user.role == 'admin':
        return redirect(url_for('admin.dashboard'))

    new_status = request.form['status']
    issue = IssueReport.query.get_or_404(issue_id)
    issue.status = new_status

    if new_status.lower() == 'resolved':
        issue.resolved_by_id = current_user.id
    else:
        issue.resolved_by_id = None

    db.session.commit()
    flash('Status updated successfully.', 'success')
    return redirect(url_for('main.ngo_dashboard'))

@main.route('/ngo/events/create', methods=['GET', 'POST'])
@login_required
def create_event():
    if current_user.role != 'ngo':
        return redirect(url_for('main.user_dashboard'))
    elif current_user.role == 'admin':
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form['description']
        date_str = request.form['date']
        location = request.form['location']
        image = request.files.get('image')

        if not title or not description or not date_str or not location:
            flash("All fields except image are required.", "danger")
            return redirect(request.url)

        try:
            event_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', 'danger')
            return redirect(request.url)

        image_filename = None
        if image and image.filename:
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
    elif current_user.role == 'admin':
        return redirect(url_for('admin.dashboard'))

    events = NGOEvent.query
    return render_template('ngo_events.html', events=events)

@main.route('/events')
@login_required
def view_events():
    if current_user.role != 'user':
        return redirect(url_for('main.ngo_events'))
    elif current_user.role == 'admin':
        return redirect(url_for('admin.dashboard'))

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
            NGOEvent.location.ilike(f"%{search}%") |
            NGOEvent.description.ilike(f"%{search}%")
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




@main.route('/user/<int:user_id>')
@login_required
def view_user_profile(user_id):
    user = User.query.get_or_404(user_id)
    posts = Post.query.filter_by(user_id=user.id).order_by(Post.timestamp.desc()).all()
    return render_template('profile/user_profile.html', user=user, posts=posts)

@main.route('/ngo/<int:user_id>')
@login_required
def ngo_profile(user_id):
    ngo = User.query.filter_by(id=user_id, role='ngo').first_or_404()
    posts = Post.query.filter_by(user_id=ngo.id).order_by(Post.timestamp.desc()).all()
    return render_template('profile/ngo_profile.html', ngo=ngo, posts=posts)



@main.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    
#    if current_user.role == 'admin':
#       return redirect(url_for('admin.dashboard'))
    if current_user.role == 'ngo':
        flash('Access denied.')
        return redirect(url_for('main.ngo_dashboard'))

    if request.method == 'POST':
        # Update name
        name = request.form.get('name')
        if name:
            current_user.name = name
        # Update bio
        bio = request.form.get('bio')
        current_user.bio = bio
        
        # Update profile photo
        
        # Handle photo upload
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo.filename != '':
                filename = secure_filename(photo.filename)
                photo.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                current_user.photo = filename
            db.session.commit()

        contrib_title = request.form.get('contrib_title')
        contrib_desc = request.form.get('contrib_description')
        if contrib_title:
            new_contrib = Contribution(
                user_id=current_user.id,
                title=contrib_title,
                description=contrib_desc
            )
            db.session.add(new_contrib)

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('main.view_user_profile', user_id=current_user.id))

    return render_template('profile/edit_profile.html', user=current_user)

@main.route('/edit_ngo_profile', methods=['GET', 'POST'])
@login_required
def edit_ngo_profile():
    if current_user.role == 'user':
        flash('Access denied.')
        return redirect(url_for('main.user_dashboard'))
    

    ngo = current_user  # assuming current_user is an NGO
    if request.method == 'POST':
        ngo.name = request.form['name']
        ngo.email = request.form['email']
        ngo.bio = request.form['bio']

        # Handle photo upload
        if 'photo' in request.files:
            photo = request.files['photo']
            if photo.filename != '':
                filename = secure_filename(photo.filename)
                photo.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                ngo.photo = filename

        db.session.commit()
        flash('NGO profile updated successfully!', 'success')
        return redirect(url_for('main.ngo_profile', user_id=current_user.id))

    return render_template('profile/edit_ngo_profile.html', ngo=ngo)




@main.route('/create_post', methods=['POST'])
@login_required
def create_post():
    title = request.form.get('title')
    image = request.files.get('image')
    file = request.files.get('file')

    image_filename = None
    file_filename = None

    if image:
        image_filename = secure_filename(image.filename)
        image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], image_filename))

    if file:
        file_filename = secure_filename(file.filename)
        file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], file_filename))

    new_post = Post(
        title=title,
        image_filename=image_filename,
        file_filename=file_filename,
        user_id=current_user.id
    )

    db.session.add(new_post)
    db.session.commit()
    flash('Post created successfully!', 'success')
    return redirect(request.referrer or url_for('main.view_user_profile', user_id=current_user.id))




@main.route('/post/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)

    if post.user_id != current_user.id:
        flash("You don't have permission to edit this post.", "danger")
        return redirect(url_for('main.view_user_profile', user_id=current_user.id))

    if request.method == 'POST':
        post.title = request.form['title']
        db.session.commit()
        flash("Post updated successfully!", "success")
        return redirect(url_for('main.view_user_profile', user_id=current_user.id))

    return render_template('post/edit_post.html', post=post)




@main.route('/post/delete/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)

    if post.user_id != current_user.id:
        flash("You don't have permission to delete this post.", "danger")
        return redirect(url_for('main.view_user_profile', user_id=current_user.id))

    db.session.delete(post)
    db.session.commit()
    flash("Post deleted successfully!", "success")
    return redirect(url_for('main.view_user_profile', user_id=current_user.id))
