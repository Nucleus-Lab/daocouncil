import os
from datetime import datetime
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Base = declarative_base()

# User model
class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    user_address = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
# Database operations for chat
def create_user(db, username: str, user_address: str):
    new_message = UserDB(
        username=username,
        user_address=user_address,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message

def get_user(db, user_address: str) -> UserDB:
    return db.query(UserDB)\
        .filter(UserDB.user_address == user_address)\
        .order_by(UserDB.created_at.asc())\
        .first()


Base.metadata.create_all(bind=engine)