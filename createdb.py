from flask_sqlalchemy import SQLAlchemy

def db_make(app):
    with app.app_context():
        db = SQLAlchemy(app)

        class Participant(db.Model):
            id = db.Column(db.Integer, primary_key=True)
            participant_id = db.Column(db.Integer(), unique=True, nullable=False)
            hash_code = db.Column(db.String(8), unique=True, nullable=False)
            played_days = db.Column(db.String(100), nullable=False, default='')
            game_data = db.relationship('GameData', backref='participant', lazy=True)
            start_date = db.Column(db.Date)  # Added start_date field
            end_date = db.Column(db.Date)    # Added end_date field
            current_game_day = db.Column(db.Integer, default=1)  # Added current_game_day field
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

        db.create_all()
    
    return db, Participant, GameStatus, GameData