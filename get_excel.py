import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Define SQLAlchemy base and engine
Base = declarative_base()
engine = create_engine('sqlite:///./instance/participants.db')

# Define Participant and GameData models
class Participant(Base):
    __tablename__ = 'participant'
    id = Column(Integer, primary_key=True)
    participant_id = Column(Integer(), unique=True, nullable=False)
    hash_code = Column(String(8), unique=True, nullable=False)
    played_days = Column(String(100), nullable=False, default='')
    start_date = Column(Date)
    end_date = Column(Date)
    current_game_day = Column(Integer, default=1)
    condition = Column(String(2), nullable=False)
    game_data = relationship('GameData', backref='participant', lazy=True)

class GameData(Base):
    __tablename__ = 'game_data'
    id = Column(Integer, primary_key=True)
    participant_id = Column(Integer, ForeignKey('participant.id'), nullable=False)
    game_day = Column(Integer, nullable=False)
    clicks = Column(Integer, nullable=False)
    selected_items = Column(Integer, nullable=False)
    total_items = Column(Integer, nullable=False)
    question_1 = Column(Integer, nullable=False)
    question_2 = Column(Integer, nullable=False)
    question_3 = Column(Integer, nullable=False)
    question_4 = Column(Integer, nullable=False)
    question_5 = Column(Integer, nullable=False)
    image_path = Column(String(256), nullable=True)

# Create all tables in the database
Base.metadata.create_all(engine)

# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()

# Query the Participant and GameData tables
participants_query = session.query(Participant).all()
game_data_query = session.query(GameData).all()

# Convert query results to pandas dataframes
participants_data = []
for participant in participants_query:
    played_days = len(participant.game_data)
    current_game_day = played_days + 1 if played_days < 8 else 8
    participant_dict = {
        'id': participant.id,
        'participant_id': participant.participant_id,
        'hash_code': participant.hash_code,
        'played_days': played_days,
        'start_date': participant.start_date,
        'end_date': participant.end_date,
        'current_game_day': current_game_day,
        'condition': participant.condition
    }
    participants_data.append(participant_dict)

participants_df = pd.DataFrame(participants_data)

game_data_list = []
for data in game_data_query:
    game_data_dict = {
        'participant_id': data.participant_id,
        f'game_day_{data.game_day}_clicks': data.clicks,
        f'game_day_{data.game_day}_selected_items': data.selected_items,
        f'game_day_{data.game_day}_total_items': data.total_items,
        f'game_day_{data.game_day}_question_1': data.question_1,
        f'game_day_{data.game_day}_question_2': data.question_2,
        f'game_day_{data.game_day}_question_3': data.question_3,
        f'game_day_{data.game_day}_question_4': data.question_4,
        f'game_day_{data.game_day}_question_5': data.question_5
    }
    game_data_list.append(game_data_dict)

game_data_df = pd.DataFrame(game_data_list)

# Merge the two dataframes on 'participant_id'
merged_df = pd.merge(participants_df, game_data_df, how='left', left_on='id', right_on='participant_id')

# Create an Excel writer and write the merged dataframe to the Excel file
with pd.ExcelWriter('participant_data.xlsx', engine='openpyxl') as writer:
    participants_df.to_excel(writer, sheet_name='Participants', index=False)
    game_data_df.to_excel(writer, sheet_name='Game Data', index=False)
    merged_df.to_excel(writer, sheet_name='Merged Data', index=False)

print('Excel file generated successfully.')
