from functools import wraps
import jwt
from app import app as application
from flask import request, jsonify
from app.users.models import User
from config import SECRET_KEY

def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message': 'a valid token is missing'})
        try:
            data = jwt.decode(token, SECRET_KEY)
            current_user = User.query.filter_by(id=data['id']).first()
        except:
            return jsonify({'message': 'token is invalid'})

        return f(current_user, *args, **kwargs)
    return decorator

def decode_auth_token(auth_token):
    try:
        payload = jwt.decode(auth_token, application.config.get('SECRET_KEY'))
        return payload['id']
    except:
        return 'bad'