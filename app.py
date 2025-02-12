from datetime import datetime
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

@app.route('/meals', methods=['POST'])
@login_required
def create_meal():
    body = request.json

    name = body.get('name')
    healthy = body.get('healthy', False)
    description = body.get('description')

    if name and description:
        meal = Meal(
            name=name,
            healthy=healthy,
            description=description,
            user_id=current_user.id,
            created_at=datetime.now()
        )

        db.session.add(meal)
        db.session.commit()

        return jsonify({ 'message': 'Meal created successfully' }), 201

@app.route('/meals', methods=['GET'])
@login_required
def get_meals():
    meals = Meal.query.filter_by(user_id=current_user.id).all()

    result = []

    for meal in meals:
        result.append({
            'id': meal.id,
            'name': meal.name,
            'healthy': meal.healthy,
            'created_at': meal.created_at,
            'description': meal.description,
        })

    return jsonify(result), 200


@app.route('/meals/<int:id>', methods=['GET'])
@login_required
def get_meal(id):
    meal = Meal.query.filter_by(id=id, user_id=current_user.id).first()

    if meal and meal.user_id != current_user.id:
        return jsonify({ 'message': 'Unauthorized' }), 403

    if meal:
        return jsonify({
            'id': meal.id,
            'name': meal.name,
            'healthy': meal.healthy,
            'created_at': meal.created_at,
            'description': meal.description,
        }), 200

    return jsonify({ 'message': 'Meal not found' }), 404

@app.route('/meals/<int:id>', methods=['PUT'])
@login_required
def update_meal(id):
    meal = Meal.query.filter_by(id=id, user_id=current_user.id).first()

    if meal and meal.user_id != current_user.id:
        return jsonify({ 'message': 'Unauthorized' }), 403

    if meal:
        body = request.json

        name = body.get('name')
        healthy = body.get('healthy', False)
        description = body.get('description')

        if name and description:
            meal.name = name
            meal.healthy = healthy
            meal.description = description

            db.session.commit()

            return jsonify({ 'message': 'Meal updated successfully' }), 200

    return jsonify({ 'message': 'Meal not found' }), 404

@app.route('/meals/<int:id>', methods=['DELETE'])
@login_required
def delete_meal(id):
    meal = Meal.query.filter_by(id=id, user_id=current_user.id).first()

    if meal and meal.user_id != current_user.id:
        return jsonify({ 'message': 'Unauthorized' }), 403

    if meal:
        db.session.delete(meal)
        db.session.commit()

        return jsonify({ 'message': 'Meal deleted successfully' }), 200

    return jsonify({ 'message': 'Meal not found' }), 404

if __name__ == '__main__':
    app.run(debug=True)