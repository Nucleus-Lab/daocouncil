from fastapi import FastAPI
from dotenv import load_dotenv
import os
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# custom modules
from backend.data_structure import ChatMessage
from backend.database.chat_message import create_chat_message, get_chat_history

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ChatMessageDB(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    discussion_id = Column(Integer, index=True)
    username = Column(String)
    user_address = Column(String)
    message = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.post("/msg")
def post_msg(request: ChatMessage):
    db = SessionLocal()
    new_message=create_chat_message(db=db, discussion_id=request.discussion_id, username=request.username, user_address=request.user_address, message=request.message)
    db.close()
    return new_message


@app.get("/msg/{discussion_id}")
def get_msg(discussion_id: int):
    db = SessionLocal()
    messages = get_chat_history(db, discussion_id)
    db.close()
    return messages