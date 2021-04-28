from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import os

# Creates a flask instance with cross-origin resource sharing
app = Flask(__name__)
app.config.from_object('config')
cors = CORS(app, resources={r'/*': {"origins": '*'}})

# Initializes the SQLalchemy database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Import blueprints (different folders) here
from app.users.controller import user_routes as user_module
from app.friends.controller import friend_routes as friend_module
from app.chats.controller import chat_routes as chat_module
app.register_blueprint(user_module)
app.register_blueprint(friend_module)
app.register_blueprint(chat_module)

# This will create the database file using SQLAlchemy
db.create_all()

@app.route('/')
def home():
    return 'Hello, world!'


# Socket stuff
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

socketio = SocketIO(app, cors_allowed_origins="*")
clients = []

@socketio.on('connect')
def on_connect():
    token = request.args.get('auth')
    data = jwt.decode(token, app.config["SECRET_KEY"])
    current_user = User.query.filter_by(id=data['id']).first()

    if(current_user):
        join_room('user' + str(current_user.id))

    # Gets and joins all of the current user rooms
    if current_user and current_user.rooms:
        rooms = current_user.rooms
        for room in rooms:
            join_room(room.id)

    messages = []
    if current_user:
        for friend in current_user.friends:

            chats = Chat.query.filter(
                or_(
                    and_(
                        Chat.user_id == current_user.id,
                        Chat.receiver_id == friend.friend_id,
                        Chat.is_group == False
                    ),
                    and_(
                        Chat.user_id == friend.friend_id,
                        Chat.receiver_id == current_user.id,
                        Chat.is_group == False
                    )
                )
            ).order_by(Chat.date_created.asc()).all()[-10:]
            messages.extend(chats)

    if current_user:
        clients.append(current_user.id)
        emit("connect", {"userInfo": {'user': current_user.serialize(), "token": token}, 'messages': [m.serialize() for m in messages]})
    else:
        emit("connect", {})


@socketio.on('message')
def on_message(data):
    token = request.args.get('auth')
    token_data = jwt.decode(token, app.config["SECRET_KEY"])
    current_user = User.query.filter_by(id=token_data['id']).first()
    current_user_rooms = current_user.rooms

    receiver_id = data['receiver']
    receiver = User.query.filter_by(id=receiver_id).first()

    room = get_common_room(current_user.rooms, receiver.rooms)
    message = create_message(current_user, data, room.id)

    # Emits the message to both users
    # Should be able to emit to just a room, but there is a bug when first adding a friend
    emit('message', {'message': message.serialize()}, room='user' + str(receiver.id))
    emit('message', {'message': message.serialize()}, room='user' + str(current_user.id))

@socketio.on('groupmessage')
def on_message(data):
    token = request.args.get('auth')
    token_data = jwt.decode(token, app.config["SECRET_KEY"])
    current_user = User.query.filter_by(id=token_data['id']).first()

    room_id =int(data['room'])

    room = Room.query.filter_by(id=room_id).first()

    if room:
        message = Chat(
            group_id=room_id,
            is_group=True,
            is_image=False,
            image_location='',
            message=data['message'],
            user_id=current_user.id,
            receiver_id=current_user.id,
            date_created=datetime.utcnow()
        )

        db.session.add(message)
        db.session.commit()

        for user in room.users:
            emit('groupmessage', {'message': message.serialize()}, room='user' + str(user.id))

@socketio.on('friend')
def on_friend(data):
    friend = User.query.filter_by(id=int(data['friendID'])).first()
    token = request.args.get('auth')
    token_data = jwt.decode(token, app.config["SECRET_KEY"])
    current_user = User.query.filter_by(id=token_data['id']).first()

    # Joins new room so user can send message if other user is not online
    if friend and current_user:
        room = get_common_room(current_user.rooms, friend.rooms)
        join_room(room)

    emit('friend', {'friend': current_user.serialize()}, room='user'+str(friend.id))

@socketio.on('joinroom')
def join_new_room(data):
    token = request.args.get('auth')
    token_data = jwt.decode(token, app.config["SECRET_KEY"])
    current_user = User.query.filter_by(id=token_data['id']).first()
    friend = User.query.filter_by(id=int(data['friendID'])).first()

    # Joins new room if user is added while both online
    room = get_common_room(current_user.rooms, friend.rooms)
    join_room(room)