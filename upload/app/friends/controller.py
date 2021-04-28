from app import db
from app import app as application
from flask import Blueprint, request, jsonify
from app.users.models import User
from app.friends.models import Friend
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
from helpers.decorators import token_required
from helpers.helpers import get_common_rooms, get_common_room, get_common_rooms_no_groups
from sqlalchemy import and_
from app.rooms.models import Room

friend_routes = Blueprint('friend', __name__, url_prefix='/friends')

# Returns the 10 most recent users, excludes current user
@friend_routes.route('/userlist', methods=['GET'])
@token_required
def get_initial_list(current_user):
    current_friend_ids = list(map(lambda x: x.friend_id, current_user.friends))
    users = User.query.order_by(User.date_created.desc()).filter(User.id != current_user.id).all()
    users = list(filter(lambda x: x.id not in current_friend_ids, users))[0:10]
    friends = list(current_user.friends)

    friend_user_models = []
    for friend in friends:
        friend_user_models.append(User.query.filter(User.id == friend.friend_id).first())

    friends = []
    for friend in friend_user_models:
        friends.append({**friend.serialize_friend(), 'room': get_common_room(friend.rooms, current_user.rooms).serialize()})

    return {
        'users': [u.serialize_friend() for u in users],
        'friends': friends
    }

@friend_routes.route('/add', methods=['POST'])
@token_required
def add_friend(current_user):
    data = request.form
    friend_id = int(request.form.get('id'))
    friend = User.query.filter_by(id=friend_id).first()
    current_friends = list(map(lambda x: x.friend_id, current_user.friends))

    if friend:
        if not friend_id in current_friends:
            new_friend = Friend(
                user_id = current_user.id,
                friend_id = friend.id,
                friend_name = friend.first_name + ' ' + friend.last_name
            )
            db.session.add(new_friend)

            new_friend2 = Friend(
                user_id = friend_id,
                friend_id = current_user.id,
                friend_name = current_user.first_name + ' ' + current_user.last_name
            )
            db.session.add(new_friend2)

            friend_user = User.query.filter_by(id=friend.id).first()

            room = Room(
                is_group=False
            )
            db.session.add(room)
            current_user.rooms.append(room)
            friend_user.rooms.append(room)

            db.session.commit()

            return {
                'friend': new_friend.serialize()
            }

    return 'Cannot add friend', 400
   

@friend_routes.route('/add/group', methods=['POST'])
@token_required
def add_group(current_user):
    data = request.form
    ids = request.form.getlist('ids[]')
    name = request.form.get('name')

    room = Room(
        is_group=True,
        name=name
    )
    for userID in ids:
        uID = int(userID)
        user = User.query.filter_by(id=uID).first()
        user.rooms.append(room)

    db.session.commit()
    

    return {
        'room': room.serialize()
    }
    

@friend_routes.route('/remove/<id>', methods=['DELETE'])
@token_required
def remove_friend(current_user, id):
    Friend.query.filter(and_(Friend.friend_id==id, Friend.user_id==current_user.id)).delete()
    Friend.query.filter(and_(Friend.friend_id==current_user.id, Friend.user_id==id)).delete()

    friend = User.query.filter(User.id==id).first()

    # Deletes shared rooms from both users
    rooms = get_common_rooms_no_groups(friend.rooms, current_user.rooms)
    for room in rooms:
        current_user.rooms.remove(room)
        friend.rooms.remove(room)
        db.session.delete(room)
    db.session.commit()

    return {
        'friend': None
    }
   

    