from flask_login import UserMixin
from .extensions import db 
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50))  # "user" or "ngo" or "admin"
    bio = db.Column(db.Text)
    photo = db.Column(db.String(100))  # profile image filename

    # Reports created by this user
    reports = db.relationship('IssueReport',
                              backref='reporter',
                              foreign_keys='IssueReport.user_id',
                              lazy=True)

    # Issues this user (NGO) resolved
    resolved_issues = db.relationship('IssueReport',
                                      backref='resolved_by_user',
                                      foreign_keys='IssueReport.resolved_by_id',
                                      lazy=True)

    # Events created by this user (NGO)
    ngo_events = db.relationship('NGOEvent',
                                 backref='creator_user',
                                 foreign_keys='NGOEvent.created_by',
                                 lazy=True)

    # Contributions made by user
    contributions = db.relationship('Contribution',
                                    backref='user',
                                    foreign_keys='Contribution.user_id',
                                    lazy=True)


class Contribution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


class IssueReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    # Reported by
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='Pending')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Optional image and location
    image_filename = db.Column(db.String(150), nullable=True)
    location = db.Column(db.String(255), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)

    # Resolved by (NGO user)
    resolved_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    resolved_by = db.relationship('User', foreign_keys=[resolved_by_id])


class NGOEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False)  
    location = db.Column(db.String(200), nullable=False)
    image_filename = db.Column(db.String(100))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Creator NGO (User with role='ngo')
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    sponsors = db.Column(db.String(300), nullable=True)



class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    image_filename = db.Column(db.String(100), nullable=True)
    file_filename = db.Column(db.String(100), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='posts')
