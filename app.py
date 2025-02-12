from flask import Flask, request, jsonify
from database import db
from models.user import User
from models.meal import Meal

from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from bcrypt import hashpw, gensalt, checkpw

app = Flask(__name__)

# UTF-8
app.config['JSON_AS_ASCII'] = False

# Database configuration
app.config['SECRET_KEY'] = 'super_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:admin123@127.0.0.1:3306/flask-dialy-diet'

# Flask-Login configuration
login_manager = LoginManager()
login_manager.login_view = '/auth/sign-in'

db.init_app(app)
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
  return User.query.get(user_id)

@app.route('/auth/sign-up', methods=['POST'])
def sign_up():
    body = request.json
    
    email = body.get('email')
    password = body.get('password')

    if email and password:
        user_with_same_email = User.query.filter_by(email=email).first()

        if user_with_same_email:
            return jsonify({'message': 'User already exists'}), 400
        
        hashed_password = hashpw(str.encode(password), gensalt())
        user = User(email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()

        return jsonify({'message': 'User created successfully'}), 201
    
@app.route('/auth/sign-in', methods=['POST'])
def sign_in():
    body = request.json

    email = body.get('email')
    password = body.get('password')

    if email and password:
        user = User.query.filter_by(email=email).first()

        if user:
            does_password_match = checkpw(str.encode(password), str.encode(user.password))

            if not does_password_match:
                return jsonify({'message': 'Invalid credentials'}), 401
            
            login_user(user)
            return jsonify({'message': 'User authenticated'}), 200
        
        return jsonify({'message': 'Invalid credentials'}), 401
        
@app.route('/auth/sign-out', methods=['POST'])
@login_required
def sign_out():
    logout_user()
    return jsonify({'message': 'User logged out'}), 200

if __name__ == '__main__':
    app.run(debug=True)