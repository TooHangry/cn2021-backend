from app import db
from app import app as application
from flask import Blueprint, request
from app.users.models import User
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
from helpers.decorators import token_required
from sqlalchemy import or_

user_routes = Blueprint('user', __name__, url_prefix='/users')


@user_routes.route('/signup', methods=['POST'])
def signup():
    data = request.form
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first()

    # Creates a new user if they are not in the database
    if not user:
        user = User(
            date_created=datetime.utcnow(),
            first_name = data.get('firstName'),
            last_name = data.get('lastName'),
            email = email,
            password = generate_password_hash(password),
            profile_picture = ''
        )
        db.session.add(user)
        db.session.commit()
        return login_user(user)

    # Returns a duplicate error code, indicating the use is in the database
    return 'Not valid', 409

@user_routes.route('/login', methods=['POST'])
def login():
    data = request.form
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first()
  
    if user and check_password_hash(user.password, password):
        return login_user(user)
    
    return 'Invalid credentials', 401

@user_routes.route('/me', methods=['GET'])
@token_required
def get_current_user(current_user):
    return {
        'user': current_user.serialize()
    }

@user_routes.route('/update/me', methods=['POST'])
@token_required
def update_current_user(current_user):
    data = request.form
    first = data.get('first')
    last = data.get('last')
    nickname = data.get('nickname')
    email = data.get('email')


    user1 = User.query.filter(User.username == nickname).first()
    user2 = User.query.filter(User.email == email).first()
    print(user1, user2)

    if user2 and user2.id != current_user.id:
        return 'That email is already taken!', 400
    elif user1 and user1.id != current_user.id:
        return 'That nickname is already taken!', 400
    else:
        current_user.first_name = data.get('first')
        current_user.last_name = data.get('last')
        current_user.username = data.get('nickname')
        current_user.email = data.get('email')
        db.session.commit()
        return {
            'user': current_user.serialize()
        }

# Logs the current user in and returns a token
def login_user(user):
    isAdmin = False
    if user.id == 1:
        isAdmin = True
    token = jwt.encode({
        'id': user.id,
        'isAdmin': isAdmin,
        'exp': datetime.utcnow() + timedelta(days=365)
    }, application.config['SECRET_KEY'])
    return {
        'token': token.decode('UTF-8'),
        'user': user.serialize()
    }, 201
