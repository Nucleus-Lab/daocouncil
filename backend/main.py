from dotenv import load_dotenv
load_dotenv()

import os
import logging
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from backend.database import SessionLocal, Base, engine
from backend.data_structure import ChatMessage, User, Debate
from backend.database.chat_message import create_chat_message, get_chat_history
from backend.database.user import create_user, get_user
from backend.database.juror import create_juror, get_jurors, get_all_juror_results
from backend.database.debate import create_debate, get_debate

logger = logging.getLogger()

# 创建所有表
Base.metadata.create_all(bind=engine)

# fastapi app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        new_user = create_user(
            db=db, 
            username=request.username, 
            user_address=request.user_address,
            debate_id=request.debate_id
        )
        db.commit()
        return {
            "username": new_user.username,
            "user_address": new_user.user_address,
            "debate_id": new_user.debate_id
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error in post_user: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.post("/debate")
def post_debate(request: Debate):
    db = SessionLocal()
    try:
        # 创建陪审团成员
        juror_ids = []
        for idx, persona in enumerate(request.jurors):
            create_juror(db=db, discussion_id=request.discussion_id, juror_id=idx, persona=persona)
            juror_ids.append(idx)

        # 创建辩论
        try:
            new_debate = create_debate(
                db=db,
                discussion_id=request.discussion_id,
                topic=request.topic,
                sides=request.sides,
                juror_ids=juror_ids,
                funding=request.funding,
                action=request.action,
                creator_address=request.creator_address
            )
            db.commit()
            # 返回完整的辩论信息
            return {
                "discussion_id": new_debate.discussion_id,
                "topic": new_debate.topic,
                "sides": request.sides,
                "action": new_debate.action,
                "funding": new_debate.funding,
                "jurors": request.jurors,
                "creator_address": new_debate.creator_address
            }
        except Exception as e:
            logger.error(f"Error in create_debate: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error creating debate: {str(e)}")
            
    except Exception as e:
        db.rollback()
        logger.error(f"Error in post_debate: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
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
