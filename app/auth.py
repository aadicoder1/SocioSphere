from flask import Blueprint, render_template, request, redirect, url_for, flash
from .models import User
from .extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already exists!")
            return redirect(url_for('auth.register'))

        hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, email=email, password=hashed_pw, role=role)

        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful! Please login.")
        return redirect(url_for('auth.login'))

    return render_template('register.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            flash("Invalid credentials!")
            return redirect(url_for('auth.login'))

        login_user(user)
        if user.role == 'ngo':
            return redirect(url_for('main.ngo_dashboard'))
        else:
            return redirect(url_for('main.user_dashboard'))

    return render_template('login.html')


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
