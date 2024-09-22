import os
import uuid
import hashlib
from flask import Flask, request, jsonify
from flask_uploads import UploadSet, configure_uploads, IMAGES
from werkzeug.utils import secure_filename
from createdb import db_make
from datetime import datetime, timedelta
import pytz
from flask_migrate import Migrate

# Assuming timezone is Toronto time (Eastern Time)
toronto_tz = pytz.timezone('America/Toronto')

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///participants.db'
app.config['UPLOADED_IMAGES_DEST'] = 'uploads/images'
images = UploadSet('images', IMAGES)
configure_uploads(app, images)

db, Participant, GameStatus, GameData = db_make(app)
migrate = Migrate(app, db) # migrate if there is any changes

@app.route('/generate_hash_code', methods=['POST'])
def generate_hash_code():
    data = request.json
    condition = data.get('condition')
    name = data.get('name')
    if condition not in ['c1', 'c2', 'c3', 'c4']:
        return jsonify({'message': 'Invalid condition'}), 400
    
    # Generate a unique ID (6-digit number)
    unique_id = str(uuid.uuid4().int)[0:6]

    # Generate hash code for the ID
    hash_code = hashlib.md5(unique_id.encode()).hexdigest()[:8]

    # Calculate start and end dates for the game session
    today_toronto = datetime.now(toronto_tz).date()
    start_date = today_toronto
    end_date = today_toronto + timedelta(days=7)

    # Store start and end dates for the game session
    participant = Participant(participant_id=unique_id, p_name=name, hash_code=hash_code, start_date=start_date, end_date=end_date, condition=condition)
    db.session.add(participant)
    db.session.commit()

    return jsonify({'id': unique_id, 'hash_code': hash_code, 'start_date': start_date.strftime('%Y-%m-%d'), 'end_date': end_date.strftime('%Y-%m-%d'), 'condition': condition}), 200

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    hash_code = data.get('hash_code')
    participant = Participant.query.filter_by(hash_code=hash_code).first()
    if participant:
        return jsonify({'message': 'Valid', 'condition': participant.condition}), 200
    else:
        return jsonify({'message': 'Unvalid'}), 403

@app.route('/check_game_status', methods=['POST'])
def check_game_status():
    data = request.json
    hash_code = data.get('hash_code')
    participant = Participant.query.filter_by(hash_code=hash_code).first()
    if not participant:
        return jsonify({'message': 'Participant not found'}), 404

    current_datetime_toronto = datetime.now(toronto_tz)
    # Check if the current time is within the allowed time range to play today's game
    if current_datetime_toronto.time() < datetime.min.time() or current_datetime_toronto.time() > datetime.max.time():
        return jsonify({'message': 'You are outside the allowed time range to play today\'s game'}), 403

    # Calculate current game day based on Toronto date and time
    days_since_start = (current_datetime_toronto.date() - participant.start_date).days
    # current_game_day = min(days_since_start + 1, 8)  # Ensure maximum of 8 days
    current_game_day = days_since_start + 1

    if current_game_day > 8:
        return jsonify({'message': 'Done', 'current_game_day': -1}), 200
    
    # Check if the game for the specified game day is already played
    game_data_exists = GameData.query.filter_by(participant_id=participant.id, game_day=current_game_day).first()
    if game_data_exists:
        return jsonify({'message': 'Already Submitted', 'current_game_day': 0}), 200

    return jsonify({'message': 'Play', 'current_game_day': current_game_day}), 200

    
@app.route('/send_game_data', methods=['POST'])
def send_game_data():
    data = request.form
    participant_hash_code = data.get('hash_code')
    game_day = data.get('game_day')
    clicks = data.get('clicks')
    selected_items = data.get('selected_items')
    total_items = data.get('total_items')
    questions = data.get('questions').split(',') # Assuming it's a list of 5 numbers
    
    submission_time = datetime.now(toronto_tz)
    # Find participant by hash code
    participant = Participant.query.filter_by(hash_code=participant_hash_code).first()
    if participant:
        # Check if game data already exists for this day
        existing_game_data = GameData.query.filter_by(participant_id=participant.id, game_day=game_day).first()
        if existing_game_data:
            return jsonify({'message': 'Game data already exists for this day'}), 400

        # Handle file upload
        image_file = request.files.get('image')
        if image_file:
            # Create directory structure
            participant_dir = os.path.join(app.config['UPLOADED_IMAGES_DEST'], participant_hash_code)
            game_day_dir = os.path.join(participant_dir, f"GameDay{game_day}")
            os.makedirs(game_day_dir, exist_ok=True)

            # Save image file
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(game_day_dir, filename)
            image_file.save(image_path)
        else:
            image_path = None

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
            question_5=questions[4],
            image_path=image_path,  # Save image path
            submit_time = submission_time
        )
        db.session.add(new_game_data)
        db.session.commit()
        return jsonify({'message': 'Game data received and saved successfully'}), 200
    else:
        return jsonify({'message': 'Participant not found'}), 404
    
if __name__ == '__main__':
    app.run(host='0.0.0.0')
