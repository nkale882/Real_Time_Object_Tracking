import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev_secret_key"
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    # Optional: if you want to connect to a database (e.g., PostgreSQL, SQLite)
    # DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///default.db')
    
    # Example of adding logging configurations, if needed
    # LOGGING_LEVEL = os.getenv('LOGGING_LEVEL', 'DEBUG')

    # You can add more variables based on your app's needs like video input source, etc.
