from dotenv import load_dotenv
load_dotenv()

import os
import logging
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import dspy

# custom modules
from backend.database import SessionLocal, Base, engine
from backend.data_structure import ChatMessage, User, Debate, Side
from backend.database.chat_message import create_chat_message, get_chat_history
from backend.database.user import create_user, get_user
from backend.database.juror import create_juror, get_jurors, get_all_juror_results, create_juror_result
from backend.database.debate import create_debate, get_debate


from backend.agents.juror import Juror

logger = logging.getLogger()

# 创建所有表
# postgres database
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
Base.metadata.create_all(bind=engine)

# dspy
model = os.getenv("MODEL")
lm = dspy.LM(model=model, api_key=os.getenv("OPENAI_API_KEY"), api_base=os.getenv("OPENAI_BASE_URL"))
dspy.configure(lm=lm)

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
        # 调试日志
        logger.info(f"Received message request: {request}")
        
        new_message = create_chat_message(
            db=db,
            discussion_id=request.discussion_id,
            user_address=request.user_address,
            message=request.message,
            stance=request.stance  # 直接使用 request.stance
        )
        db.commit()
        
        debate_info = get_debate(db, request.discussion_id)
        past_messages = get_chat_history(db, request.discussion_id)
        jurors = get_jurors(db, request.discussion_id)
        
        conv_history = ""
        for msg in past_messages:
            user = get_user(db, msg.user_address)
            conv_history += f"{user.username}: {msg.message}\n"
        
        sides = []
        for idx, side in enumerate(debate_info.sides):
            sides.append(Side(id=str(idx), description=side))
        
        results = {}
        for juror_db in jurors:
            juror = Juror(persona=juror_db.persona)
            result, reasoning = juror.judge(topic=debate_info.topic, sides=sides, conv=conv_history)
            results[juror_db.juror_id] = {
                "result": result,
                "reasoning": reasoning
            }
            create_juror_result(db=db, discussion_id=request.discussion_id, latest_msg_id=new_message.id, juror_id=juror_db.juror_id, result=result, reasoning=reasoning)
            
        return results
    
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating message: {str(e)}")
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
                timestamp=res.created_at,
                stance=res.stance  # 添加 stance 到返回的消息中
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
