from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.models import User, NGOEvent, IssueReport, Post, Contribution
from app.extensions import db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role != 'admin':
        return redirect(url_for('main.index'))

    # Separate pagination for each section
    user_page = request.args.get('user_page', 1, type=int)
    ngo_page = request.args.get('ngo_page', 1, type=int)
    report_page = request.args.get('report_page', 1, type=int)
    post_page = request.args.get('post_page', 1, type=int)
    contribution_page = request.args.get('contribution_page', 1, type=int)

    users = User.query.paginate(page=user_page, per_page=5)
    ngos = NGOEvent.query.paginate(page=ngo_page, per_page=5)
    reports = IssueReport.query.paginate(page=report_page, per_page=5)
    posts = Post.query.paginate(page=post_page, per_page=5)
    contributions = Contribution.query.paginate(page=contribution_page, per_page=5)

    return render_template(
        'admin/dashboard.html',
        users=users,
        ngos=ngos,
        reports=reports,
        posts=posts,
        contributions=contributions
    )


@admin_bp.route('/promote/<int:user_id>', methods=['POST'])
@login_required
def promote_user(user_id):
    if current_user.role != 'admin':
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(user_id)
    user.role = 'admin'
    db.session.commit()
    flash('User promoted to admin!', 'success')
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/edit_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    if current_user.role != 'admin':
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/edit_user.html', user=user)


@admin_bp.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        return redirect(url_for('main.index'))
    
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!', 'danger')
    return redirect(url_for('admin.dashboard'))
