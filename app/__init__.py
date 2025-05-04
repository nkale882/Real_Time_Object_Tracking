from flask import Flask
from .settings import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Import routes after creating the app to avoid circular imports
    from .routes import main_bp 
    app.register_blueprint(main_bp)
   
    return app