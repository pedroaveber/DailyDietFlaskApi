from database import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
  __tablename__ = 'users'

  # id (int), username (str), password (str), role (str)
  id = db.Column(db.Integer, primary_key = True)
  password = db.Column(db.String(80), nullable = False)
  email = db.Column(db.String(80), unique = True, nullable = False)

  meals = db.relationship('Meal', backref = 'user', lazy = True)