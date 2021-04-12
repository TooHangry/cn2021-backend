from app import app
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import Blueprint

from run import socketio
socket_routes = Blueprint('socket', __name__, url_prefix='/socket')


# SocketIO init
# Socket Routes
