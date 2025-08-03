from flask import Flask

def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = 'supersecretkey'  # for sessions & auth

    from .routes import main
    app.register_blueprint(main)

    return app
