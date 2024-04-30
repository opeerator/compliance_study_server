import uuid
import hashlib
from flask import Flask, request, jsonify
from createdb import db_make
from datetime import datetime, timedelta
import pytz

# Assuming timezone is Toronto time (Eastern Time)
toronto_tz = pytz.timezone('America/Toronto')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///participants.db'
db, Participant, GameStatus, GameData = db_make(app)

@app.route('/generate_hash_code', methods=['GET'])
def generate_hash_code():
    # Generate a unique ID (6-digit number)
    unique_id = str(uuid.uuid4().int)[0:6]

    # Generate hash code for the ID
    hash_code = hashlib.md5(unique_id.encode()).hexdigest()[:8]

    # Calculate start and end dates for the game session
    today_toronto = datetime.now(toronto_tz).date()
    start_date = today_toronto
    end_date = today_toronto + timedelta(days=7)

    # Store start and end dates for the game session
    participant = Participant(participant_id=unique_id, hash_code=hash_code, start_date=start_date, end_date=end_date)
    db.session.add(participant)
    db.session.commit()

    return jsonify({'id': unique_id, 'hash_code': hash_code, 'start_date': start_date.strftime('%Y-%m-%d'), 'end_date': end_date.strftime('%Y-%m-%d')}), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    hash_code = data.get('hash_code')

    participant = Participant.query.filter_by(hash_code=hash_code).first()
    if participant:
        return jsonify({'message': 'Access'}), 200
    else:
        return jsonify({'message': 'Deny'}), 400

@app.route('/check_game_status', methods=['GET'])
def check_game_status():
    data = request.json
    hash_code = data.get('hash_code')

    participant = Participant.query.filter_by(hash_code=hash_code).first()
    if participant:
        # Get current date and time in Toronto time zone
        current_datetime_toronto = datetime.now(toronto_tz)

        # Check if participant is within the allowed time range to play today's game
        if current_datetime_toronto.time() >= datetime.min.time() and current_datetime_toronto.time() <= datetime.max.time():
            # Calculate current game day based on Toronto date and time
            days_since_start = (current_datetime_toronto.date() - participant.start_date).days
            current_game_day = min(days_since_start + 1, 8)  # Ensure maximum of 8 days

            return jsonify({'message': 'You can play today\'s game', 'current_game_day': current_game_day}), 200
        else:
            return jsonify({'message': 'You are outside the allowed time range to play today\'s game'}), 403
    else:
        return jsonify({'message': 'Participant not found'}), 404
    
@app.route('/send_game_data', methods=['POST'])
def send_game_data():
    data = request.json
    participant_hash_code = data.get('hash_code')
    game_day = data.get('game_day')
    clicks = data.get('clicks')
    selected_items = data.get('selected_items')
    total_items = data.get('total_items')
    questions = data.get('questions')  # Assuming it's a list of 5 numbers

    # Find participant by hash code
    participant = Participant.query.filter_by(hash_code=participant_hash_code).first()
    if participant:
        # Check if game data already exists for this day
        existing_game_data = GameData.query.filter_by(participant_id=participant.id, game_day=game_day).first()
        if existing_game_data:
            return jsonify({'message': 'Game data already exists for this day'}), 400

        new_game_data = GameData(
            participant_id=participant.id,
            game_day=game_day,
            clicks=clicks,
            selected_items=selected_items,
            total_items=total_items,
            question_1=questions[0],
            question_2=questions[1],
            question_3=questions[2],
            question_4=questions[3],
            question_5=questions[4]
        )
        db.session.add(new_game_data)
        db.session.commit()
        return jsonify({'message': 'Game data received and saved successfully'}), 200
    else:
        return jsonify({'message': 'Participant not found'}), 404
    
if __name__ == '__main__':
    app.run(debug=True)
