from database import db
from flask_login import UserMixin

class Meal(db.Model, UserMixin):
  __tablename__ = 'meals'

  # id (int), name (str), description (str), created_at (datetime), healthy (bool), user_id (int)
  id = db.Column(db.Integer, primary_key = True)
  name = db.Column(db.String(80), nullable = False)
  description = db.Column(db.String(255), nullable = False)
  created_at = db.Column(db.DateTime, nullable = False)
  healthy = db.Column(db.Boolean, nullable = False)
  user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)