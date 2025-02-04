from dotenv import load_dotenv
from datetime import datetime
from typing import List
import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

load_dotenv()

# Get DATABASE_URL and ensure it starts with "postgresql://"
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Create SQLAlchemy engine and session factory
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Chat model
class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    discussion_id = Column(Integer, index=True)
    username = Column(String)
    user_address = Column(String)
    message = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create all tables
Base.metadata.create_all(bind=engine)

# Database operations for chat
def create_chat_message(db, discussion_id: int, username: str, user_address: str, message: str):
    new_message = ChatMessage(
        discussion_id=discussion_id,
        username=username,
        user_address=user_address,
        message=message,
        created_at=datetime.utcnow()
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message

def get_chat_history(db, discussion_id: int) -> List[ChatMessage]:
    return db.query(ChatMessage)\
        .filter(ChatMessage.discussion_id == discussion_id)\
        .order_by(ChatMessage.created_at.asc())\
        .all()

def main():
    db = SessionLocal()
    try:
        # Create some test messages
        create_chat_message(db, discussion_id=1, user="Alice", message="Hello!")
        create_chat_message(db, discussion_id=1, user="Bob", message="Hi Alice!")
        
        # Get chat history
        history = get_chat_history(db, discussion_id=1)
        print("\nChat History:")
        for msg in history:
            print(f"[{msg.created_at}] {msg.user}: {msg.message}")

    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()

