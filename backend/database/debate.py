import os
from datetime import datetime
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Base = declarative_base()

# Juror model
class DebateDB(Base):
    __tablename__ = "debates"

    id = Column(Integer, primary_key=True, index=True)
    discussion_id = Column(Integer, index=True)
    topic = Column(String)
    sides = Column(String)  # List of strings stored as JSON string
    juror_ids = Column(String)
    funding = Column(Integer)
    action = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


# Database operations for debate
def create_debate(db, discussion_id: int, topic: str, sides: list[str], juror_ids: list[int], funding: int, action: str):
    new_debate = DebateDB(
        discussion_id=discussion_id,
        topic=topic,
        sides=sides,
        juror_ids=juror_ids,
        funding=funding,
        action=action,
        created_at=datetime.utcnow()
    )
    db.add(new_debate)
    db.commit()
    db.refresh(new_debate)
    return new_debate

def get_debate(db, discussion_id: int) -> DebateDB:
    return db.query(DebateDB).filter(DebateDB.discussion_id == discussion_id).first()

Base.metadata.create_all(bind=engine)