from flask import Flask
import os
import secrets
from .models import db
from .routes import configure_routes

# Try to load .env file if python-dotenv is installed
try:
    from dotenv import load_dotenv # type: ignore
    load_dotenv()
    print("✅ Loaded environment variables from .env file")
except ImportError:
    print("ℹ️ python-dotenv not installed, skipping .env file loading")

app = Flask(__name__)

# Database configuration
db_url = os.getenv("DATABASE_URL")
if not db_url:
    print("⚠️ No DATABASE_URL found, using SQLite as fallback")
    db_url = "sqlite:////data/my-eurovision-table.db"
else:
    print(f"✅ Using database: {db_url.split('@')[1] if '@' in db_url else db_url}")

# Use environment variable for secret key with a secure random fallback for development
secret_key = os.getenv("SECRET_KEY")
if not secret_key:
    secret_key = secrets.token_hex(16)
    print("⚠️ No SECRET_KEY found, generated random key for this session")
else:
    print("✅ Using provided SECRET_KEY")

# Configure Flask app
app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = secret_key

# Check if we should auto-initialize the database with Eurovision data
AUTO_INIT_DB = os.getenv('AUTO_INIT_DB', '0') == '1'
if AUTO_INIT_DB:
    print("✅ AUTO_INIT_DB is enabled - will check if database needs initialization")

# Initialize database
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
            print("🔄 Database is empty - initializing with Eurovision data")
            initialize_database()
        else:
            print("ℹ️ Database already contains data - skipping auto-initialization")

configure_routes(app)
