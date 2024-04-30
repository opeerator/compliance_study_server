import pandas as pd
from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Define SQLAlchemy base and engine
Base = declarative_base()
engine = create_engine('sqlite:///participants.db')

# Define Participant and GameData models
class Participant(Base):
    __tablename__ = 'participant'
    id = Column(Integer, primary_key=True)
    hash_code = Column(String(8), unique=True, nullable=False)
    played_days = Column(String(100), nullable=False, default='')
    game_data = relationship('GameData', backref='participant', lazy=True)
    start_date = Column(Date)
    end_date = Column(Date)
    current_game_day = Column(Integer, default=1)

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

# Create all tables in the database
Base.metadata.create_all(engine)

# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()

# Query the Participant and GameData tables
participants_query = session.query(Participant).all()
game_data_query = session.query(GameData).all()

# Convert query results to pandas dataframes
participants_df = pd.DataFrame([vars(participant) for participant in participants_query])
game_data_df = pd.DataFrame([vars(data) for data in game_data_query])

# Create an Excel writer and write dataframes to the Excel file
with pd.ExcelWriter('participant_data.xlsx', engine='openpyxl') as writer:
    participants_df.to_excel(writer, sheet_name='Participants', index=False)
    game_data_df.to_excel(writer, sheet_name='Game Data', index=False)

print('Excel file generated successfully.')
