from app import db
from app import app as application
from flask import Blueprint, request
from app.chats.models import Chat
import jwt
from datetime import datetime, timedelta
from helpers.decorators import token_required
from sqlalchemy import or_, and_

chat_routes = Blueprint('chat', __name__, url_prefix='/chats')

@chat_routes.route('/loadinitial')
@token_required
def send_chat(current_user):
    friendIDs = list(map(lambda x: x.friend_id, list(current_user.friends)))

    messages = []
    for friendID in friendIDs:
        chats = Chat.query.filter(
            or_(
                and_(
                    Chat.user_id == current_user.id,
                    Chat.receiver_id == friendID,
                    Chat.is_group == False
                ),
                and_(
                    Chat.user_id == friendID,
                    Chat.receiver_id == current_user.id,
                    Chat.is_group == False
                )
            )
        ).order_by(Chat.date_created.asc()).all()[-10:]
        messages.extend(chats)
    return {
        'messages': [m.serialize() for m in messages]
    }

@chat_routes.route('/loadinitialgroup')
@token_required
def load_group_chats(current_user):
    rooms = current_user.rooms
    groupIDS = list(filter(lambda x: x.is_group, rooms))

    messages = []
    for group in groupIDS:
        chats = Chat.query.filter(
                and_(
                    Chat.is_group == True,
                    Chat.group_id == group.id
                )
        ).order_by(Chat.date_created.asc()).all()[-10:]
        messages.extend(chats)

    return {
        'messages': [m.serialize() for m in messages]
    }

    

def create_message(current_user, message_data, room=0):
    message = message_data['message']
    receiver_id = message_data['receiver']

    if message:
        chat = Chat(
            is_group=False,
            group_id=room,
            is_image=False,
            user_id=current_user.id,
            receiver_id=receiver_id,
            message=message,
            date_created=datetime.utcnow()
        )
        db.session.add(chat)
        db.session.commit()
        return chat
    return None