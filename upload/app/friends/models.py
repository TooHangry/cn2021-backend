from app import db
from sqlalchemy.orm import relationship
import os
from app.users.models import User

class Friend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = relationship('User', back_populates='friends')
    friend_id = db.Column(db.Integer)
    friend_name = db.Column(db.String(128))

    def serialize(self):
        friend = User.query.filter(User.id == self.friend_id).first()
        return {
            'id': self.id,
            'userID': self.user_id,
            'friendID': self.friend_id,
            'username': friend.username,
            'name': self.friend_name
        }

    