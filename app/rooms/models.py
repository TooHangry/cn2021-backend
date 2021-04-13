from app import db
from sqlalchemy.orm import relationship
import os

users_to_rooms = db.Table('users_to_rooms',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('room_id', db.Integer, db.ForeignKey('room.id')),
    )

class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    is_group = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(80))

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'isGroup': self.is_group
        }
