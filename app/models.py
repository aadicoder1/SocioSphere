from flask_login import UserMixin
from .extensions import db 
from datetime import datetime


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(50))  # "user" or "ngo"


class IssueReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default='Pending')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    image_filename = db.Column(db.String(150), nullable=True)
    location = db.Column(db.String(255), nullable=True)  # optional readable location name
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    user = db.relationship('User', backref=db.backref('reports', lazy=True))


class NGOEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False)  
    location = db.Column(db.String(200), nullable=False)
    image_filename = db.Column(db.String(100))
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    creator = db.relationship('User', backref=db.backref('ngo_events', lazy=True))