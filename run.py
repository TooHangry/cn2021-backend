from flask_socketio import SocketIO, emit, join_room
from flask import request
import jwt
from app import app, db
from app.users.models import User
from app.rooms.models import Room
from app.chats.controller import create_message
from datetime import datetime


socketio = SocketIO(app, cors_allowed_origins="*")
clients = []

def get_common_room(user1, user2):

    print(user1.all(), user2.all())
    for room in user1:
        if room in user2:
            return room

    return None


@socketio.on('connect')
def on_connect():
    token = request.args.get('auth')
    data = jwt.decode(token, app.config["SECRET_KEY"])
    current_user = User.query.filter_by(id=data['id']).first()

    # Gets and joins all of the current user rooms
    if current_user and current_user.rooms:
        rooms = current_user.rooms
        for room in rooms:
            join_room(room.id)

    if current_user:
        clients.append(current_user.id)
        emit("connect", {"conncted id": current_user.serialize()})
    else:
        emit("connect", {"conncted id": token})

@socketio.on('message')
def on_message(data):
    token = request.args.get('auth')
    token_data = jwt.decode(token, app.config["SECRET_KEY"])
    current_user = User.query.filter_by(id=token_data['id']).first()
    current_user_rooms = current_user.rooms


    print(current_user_rooms)

    receiver_id = data['receiver']
    receiver = User.query.filter_by(id=receiver_id).first()
    room = get_common_room(current_user.rooms, receiver.rooms)
    
    message = create_message(current_user, data)

    print(message, room)
    # if message:
    #     print(message.serialize())
    #     emit('message', {'message': message.serialize()}, room=room['id'])
    # else:
    #     emit('message', {})



socketio.run(app, host='0.0.0.0', port=8080, debug=True)
