from flask import Flask
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



