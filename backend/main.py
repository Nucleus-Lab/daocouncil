from dotenv import load_dotenv
load_dotenv()

import os
from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from typing import List
import logging

logger = logging.getLogger()


# custom modules
from backend.data_structure import ChatMessage, User, Debate
from backend.database.chat_message import create_chat_message, get_chat_history
from backend.database.user import create_user, get_user
from backend.database.juror import create_juror, get_jurors, get_all_juror_results
from backend.database.debate import create_debate, get_debate

# postgres database
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
Base.metadata.create_all(bind=engine)

# fastapi app
app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

@app.post("/msg")
def post_msg(request: ChatMessage):
    db = SessionLocal()
    try:
        new_message = create_chat_message(db=db, discussion_id=request.discussion_id, user_address=request.user_address, message=request.message)
        db.commit()
        return new_message
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating message: {str(e)}")
        raise HTTPException(status_code=500, detail="Error creating message")
    finally:
        db.close()

@app.get("/msg/{discussion_id}", response_model=List[ChatMessage])
def get_msg(discussion_id: int):
    db = SessionLocal()
    try:
        response = get_chat_history(db, discussion_id)
        messages = []
        for res in response:
            user_address = res.user_address
            user = get_user(db, user_address)
            messages.append(ChatMessage(
                discussion_id=res.discussion_id,
                username=user.username,
                user_address=user_address,
                message=res.message,
                timestamp=res.created_at
            ))
        return messages
    except Exception as e:
        logger.error(f"Error getting messages: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving messages")
    finally:
        db.close()

@app.post("/user")
def post_user(request: User):
    db = SessionLocal()
    try:
        new_user = create_user(db, request.username, request.user_address)
        db.commit()
        return new_user
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=500, detail="Error creating user")
    finally:
        db.close()

@app.post("/debate")
def post_debate(request: Debate):
    db = SessionLocal()
    try:
        juror_ids = []
        for idx, persona in enumerate(request.jurors):
            create_juror(db=db, discussion_id=request.discussion_id, juror_id=idx, persona=persona)
            juror_ids.append(idx)
        new_debate = create_debate(
            db=db,
            discussion_id=request.discussion_id,
            topic=request.topic,
            sides=request.sides,
            juror_ids=juror_ids,
            funding=request.funding,
            action=request.action
        )
        db.commit()
        return new_debate
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating debate: {str(e)}")
        raise HTTPException(status_code=500, detail="Error creating debate")
    finally:
        db.close()

@app.get("/debate/{discussion_id}")
def return_debate_info(discussion_id: str):
    db = SessionLocal()
    try:
        debate = get_debate(db, discussion_id)
        jurors = get_jurors(db, discussion_id)
        return {"debate": debate, "jurors": jurors}
    except Exception as e:
        logger.error(f"Error getting debate info: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving debate information")
    finally:
        db.close()

@app.get("/juror_results/{discussion_id}")
def return_juror_results(discussion_id: int):
    db = SessionLocal()
    try:
        juror_results = get_all_juror_results(db, discussion_id)
        return juror_results
    except Exception as e:
        logger.error(f"Error getting juror results: {str(e)}")
        raise HTTPException(status_code=500, detail="Error retrieving juror results")
    finally:
        db.close()
