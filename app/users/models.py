from app import db
from sqlalchemy.orm import relationship
import os
from app.rooms.models import users_to_rooms
from helpers.helpers import get_common_room

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime(timezone=False))
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    username = db.Column(db.String(80))
    email = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80))
    profile_picture = db.Column(db.String(50))

    # Expansion properties
    friends = relationship('Friend', back_populates='user', lazy='dynamic')
    chats = relationship('Chat', back_populates='user', lazy='dynamic')
    rooms = relationship('Room', secondary=users_to_rooms, backref=db.backref('users', lazy='dynamic'))

    def serialize(self):
        name = str(self.first_name) + ' ' + str(self.last_name)
        return {
            'id': self.id,
            'name': name,
            'username': self.username,
            'email': self.email,
            'profilePicture': self.profile_picture,
            'friends': get_friends(self),
            'rooms': [r.serialize() for r in self.rooms]
        }

    def serialize_friend(self):
        name = str(self.first_name) + ' ' + str(self.last_name)
        return {
            'id': self.id,
            'username': self.username,
            'name': name,
            'profilePicture': self.profile_picture,
        }

def get_friends(user):
    friend_user_models = []
    for friend in user.friends:
        friend_user_models.append(User.query.filter(User.id == friend.friend_id).first())

    mapped_friends = []
    for friend in friend_user_models:
        mapped_friends.append({**friend.serialize_friend(), 'room': get_common_room(friend.rooms, user.rooms).serialize()})
        
    return mapped_friends