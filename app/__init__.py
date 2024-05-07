from flask import Flask
import os
from .models import db
from .routes import configure_routes

app = Flask(__name__)

db_url = os.getenv("DATABASE_URL") or "sqlite:////data/my-eurovision-table.db"

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key'  # Change this to a real secret key in production

db.init_app(app)

with app.app_context():
    db.create_all()

configure_routes(app)
