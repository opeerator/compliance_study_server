from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz

db = SQLAlchemy()
# Assuming timezone is Toronto time (Eastern Time)
toronto_tz = pytz.timezone('America/Toronto')
submission_time = datetime.now(toronto_tz)

class Participant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer(), unique=True, nullable=False)
    p_name = db.Column(db.String(), unique=False, nullable=False)
    hash_code = db.Column(db.String(8), unique=True, nullable=False)
    played_days = db.Column(db.String(100), nullable=False, default='')
    game_data = db.relationship('GameData', backref='participant', lazy=True)
    start_date = db.Column(db.Date)  # Added start_date field
    end_date = db.Column(db.Date)    # Added end_date field
    current_game_day = db.Column(db.Integer, default=1)  # Added current_game_day field
    condition = db.Column(db.String(2), nullable=False)  # Added condition field

class GameStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.Integer, nullable=False)
    played = db.Column(db.String(100), nullable=False, default='')

class GameData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    participant_id = db.Column(db.Integer, db.ForeignKey('participant.id'), nullable=False)
    game_day = db.Column(db.Integer, nullable=False)
    clicks = db.Column(db.Integer, nullable=False)
    selected_items = db.Column(db.Integer, nullable=False)
    total_items = db.Column(db.Integer, nullable=False)
    question_1 = db.Column(db.Integer, nullable=False)
    question_2 = db.Column(db.Integer, nullable=False)
    question_3 = db.Column(db.Integer, nullable=False)
    question_4 = db.Column(db.Integer, nullable=False)
    question_5 = db.Column(db.Integer, nullable=False)
    image_path = db.Column(db.String(256), nullable=True)  # Add this line
    timestamp = db.Column(db.DateTime, nullable=False, default=submission_time)  # Add timestamp field

def db_make(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
    return db, Participant, GameStatus, GameData
