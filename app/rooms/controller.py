from app import db
from app import app as application
from flask import Blueprint
from helpers.decorators import token_required

room_routes = Blueprint('room', __name__, url_prefix='/rooms')

@room_routes.route('/getgroups', methods=['GET'])
@token_required
def get_rooms(current_user):
    rooms = current_user.rooms
    groups = list(filter(lambda x: x.is_group, rooms))

    return {
        'rooms': [r.serialize() for r in groups]
    }



