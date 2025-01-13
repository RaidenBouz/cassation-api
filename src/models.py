from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"User: {self.username}"

class Decision(db.Model):
    __tablename__ = 'decisions'
    id = db.Column(db.String, primary_key=True)
    title = db.Column(db.String, nullable=True)
    formation = db.Column(db.String, nullable=True)
    content = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f"Decision: {self.id}"