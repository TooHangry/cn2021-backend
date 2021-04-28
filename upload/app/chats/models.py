from app import db
from sqlalchemy.orm import relationship
import os

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, default=0)
    is_group = db.Column(db.Boolean, default=False)
    is_image = db.Column(db.Boolean, default=False)
    image_location = db.Column(db.String(120), nullable=True)
    message = db.Column(db.String(120), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = relationship('User', back_populates='chats')
    receiver_id = db.Column(db.Integer, nullable=True, default=0)
    date_created = db.Column(db.DateTime(timezone=False))

    def serialize(self):
        username = self.user.first_name + ' ' + self.user.last_name
        if self.user.username:
            username = self.user.username


        return {
            'id': self.id,
            'isGroup': self.is_group,
            'roomID': self.group_id,
            'isImage': self.is_image,
            'imageLocation': self.image_location,
            'userID': self.user_id,
            'receiverID': self.receiver_id,
            'dateCreated': str(self.date_created),
            'message': self.message,
            'username': username
        }