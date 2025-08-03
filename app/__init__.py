from flask import Flask
from .extensions import db
from flask_login import LoginManager


def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = 'supersecretkey'  # for sessions & auth

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    
    db.init_app(app)
    from .models import User
    from .report import report_bp
    from .auth import auth
    from .routes import main

    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(report_bp)
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    

    return app
