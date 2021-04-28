from flask_socketio import SocketIO, emit, join_room
from flask import request
import jwt
from app import app, db
from app.users.models import User
from app.rooms.models import Room
from app.chats.models import Chat
from app.chats.controller import create_message
from datetime import datetime
from helpers.helpers import get_common_room
from sqlalchemy import or_, and_


from app import socketio, app



socketio.run(app, host='0.0.0.0', port=8080, debug=True)
