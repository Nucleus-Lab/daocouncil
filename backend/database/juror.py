import os
from datetime import datetime
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Base = declarative_base()

# Juror model
class JurorDB(Base):
    __tablename__ = "jurors"

    id = Column(Integer, primary_key=True, index=True)
    juror_id = Column(Integer, index=True)
    discussion_id = Column(Integer, index=True)
    persona = Column(String)

class JurorResultDB(Base):
    __tablename__ = "juror_results"

    id = Column(Integer, primary_key=True, index=True)
    juror_id = Column(Integer, index=True)
    discussion_id = Column(Integer, index=True)
    latest_msg_id = Column(Integer, index=True)
    result = Column(String)
    reasoning = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

# Database operations for juror
def create_juror(db, discussion_id: int, juror_id: int, persona: str):
    new_juror = JurorDB(
        discussion_id=discussion_id,
        juror_id=juror_id,
        persona=persona,
    )
    db.add(new_juror)
    db.commit()
    db.refresh(new_juror)
    return new_juror


def get_jurors(db, discussion_id: int) -> List[JurorDB]:
    jurors = db.query(JurorDB).filter(JurorDB.discussion_id == discussion_id).all()
    return jurors

def create_juror_result(db, juror_id: int, discussion_id: int, latest_msg_id: int, result: str, reasoning: str):
    new_message = JurorResultDB(
        juror_id=juror_id,
        discussion_id=discussion_id,
        latest_msg_id=latest_msg_id,
        result=result,
        reasoning=reasoning,
        created_at=datetime.utcnow()
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message

def get_juror_result(db, juror_id: int, discussion_id: int) -> List[JurorResultDB]:
    return db.query(JurorResultDB)\
        .filter(JurorResultDB.juror_id == juror_id)\
        .filter(JurorResultDB.discussion_id == discussion_id)\
        .order_by(JurorResultDB.created_at.asc())\
        .all()
        
def get_all_juror_results(db, discussion_id: int) -> List[List[JurorResultDB]]:
    # get all juror ids where discussion id is the same
    juror_ids = db.query(JurorResultDB.juror_id).filter(JurorResultDB.discussion_id == discussion_id).distinct().all()
    # get all juror results for each juror id
    juror_results = []
    for juror_id in juror_ids:
        juror_results.append(get_juror_result(db, juror_id, discussion_id))
    return juror_results

Base.metadata.create_all(bind=engine)