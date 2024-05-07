from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

association_table = db.Table('association',
    db.Column('stage_id', db.Integer, db.ForeignKey('stage.id'), primary_key=True),
    db.Column('country_id', db.Integer, db.ForeignKey('country.id'), primary_key=True)
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    grades = db.relationship('Grade', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

class Stage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    display_name = db.Column(db.String(128), nullable=False)
    countries = db.relationship('Country', secondary=association_table, back_populates='stages')
    grades = db.relationship('Grade', backref='stage', lazy=True)

    def __repr__(self):
        return f'<Stage {self.display_name}>'

class Country(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    display_name = db.Column(db.String(128), nullable=False)
    artist = db.Column(db.String(128), nullable=False)
    song = db.Column(db.String(128), nullable=False)
    stages = db.relationship('Stage', secondary=association_table, back_populates='countries')
    grades = db.relationship('Grade', backref='country', lazy=True)

    def __repr__(self):
        return f'<Country {self.display_name}>'

class Grade(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    stage_id = db.Column(db.Integer, db.ForeignKey('stage.id'), nullable=False)
    country_id = db.Column(db.Integer, db.ForeignKey('country.id'), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def __repr__(self):
        return f'<Grade {self.value} by User {self.user_id} for Country {self.country_id} on Stage {self.stage_id}>'
