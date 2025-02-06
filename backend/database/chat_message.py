import os
from datetime import datetime
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Base = declarative_base()

# Chat model
class ChatMessageDB(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    discussion_id = Column(Integer, index=True)
    user_address = Column(String)
    message = Column(String)
    stance = Column(String, nullable=True)  # 添加 stance 字段，允许为空
    created_at = Column(DateTime, default=datetime.utcnow)

# Database operations for chat
def create_chat_message(db, discussion_id: int, user_address: str, message: str, stance: Optional[str] = None):
    new_message = ChatMessageDB(
        discussion_id=discussion_id,
        user_address=user_address,
        message=message,
        stance=stance,
        created_at=datetime.utcnow()
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message

def get_chat_history(db, discussion_id: int) -> List[ChatMessageDB]:
    return db.query(ChatMessageDB)\
        .filter(ChatMessageDB.discussion_id == discussion_id)\
        .order_by(ChatMessageDB.created_at.asc())\
        .all()


Base.metadata.create_all(bind=engine)