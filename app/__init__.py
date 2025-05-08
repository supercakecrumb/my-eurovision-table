from flask import Flask
import os
import secrets
from .models import db
from .routes import configure_routes

app = Flask(__name__)

db_url = os.getenv("DATABASE_URL") or "sqlite:////data/my-eurovision-table.db"

# Use environment variable for secret key with a secure random fallback for development
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY") or secrets.token_hex(16)

# Check if we should auto-initialize the database with Eurovision data
AUTO_INIT_DB = os.getenv('AUTO_INIT_DB', '0') == '1'

db.init_app(app)

with app.app_context():
    # Create database tables
    db.create_all()
    
    # Check if we should initialize with data
    if AUTO_INIT_DB:
        # Only import db_init if we need it (to avoid circular imports)
        from .db_init import initialize_database
        
        # Check if the database is empty (no stages)
        from .models import Stage
        if Stage.query.count() == 0:
            print("🔄 AUTO_INIT_DB is enabled - initializing database with Eurovision data")
            initialize_database()
        else:
            print("ℹ️ Database already contains data - skipping auto-initialization")

configure_routes(app)
