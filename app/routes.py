from flask import Blueprint, render_template
from flask_login import login_required, current_user

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
    return render_template('ngo_dashboard.html', name=current_user.username)
