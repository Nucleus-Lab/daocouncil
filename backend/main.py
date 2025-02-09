from dotenv import load_dotenv
load_dotenv()

import os
import logging
from typing import List, Dict
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import dspy
import asyncio
from httpx import AsyncClient
import datetime
import json

# custom modules
from backend.database import SessionLocal, Base, engine
from backend.data_structure import ChatMessage, User, Debate, Side, GeneratePersonasRequest
from backend.database.chat_message import create_chat_message, get_chat_history, ChatMessageDB
from backend.database.user import create_user, get_user
from backend.database.juror import create_juror, get_jurors, get_juror_result, get_all_juror_results, create_juror_result
from backend.database.debate import create_debate, get_debate, DebateDB
from backend.agents.juror import Juror, generate_juror_persona
from backend.debate_manager.debate_manager import DebateManager
from backend.debate_manager.wallet_storage import get_debate_wallets

# Constants
JUDGE_API_URL = os.getenv("JUDGE_API_URL", "http://localhost:8001")

logger = logging.getLogger()

# Create singleton DebateManager instance
debate_manager = DebateManager(debate_id=None, api_url=JUDGE_API_URL)

# dspy
model = os.getenv("MODEL")
lm = dspy.LM(model=model, api_key=os.getenv("OPENAI_API_KEY"), api_base=os.getenv("OPENAI_BASE_URL"))
dspy.configure(lm=lm)

# fastapi app
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store connected WebSocket clients
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}  # debate_id -> {client_id: websocket}

    async def connect(self, websocket: WebSocket, debate_id: str, client_id: str):
        await websocket.accept()
        if debate_id not in self.active_connections:
            self.active_connections[debate_id] = {}
        self.active_connections[debate_id][client_id] = websocket

    def disconnect(self, debate_id: str, client_id: str):
        if debate_id in self.active_connections:
            self.active_connections[debate_id].pop(client_id, None)
            if not self.active_connections[debate_id]:
                self.active_connections.pop(debate_id, None)

    async def broadcast_message(self, debate_id: str, message: dict):
        if debate_id in self.active_connections:
            for connection in self.active_connections[debate_id].values():
                try:
                    await connection.send_json(message)
                except:
                    # Handle failed connections
                    continue

manager = ConnectionManager()


def wrap_message(message: ChatMessageDB):
    return {
        "type": "new_message",
        "data": {
            "id": message.id,
            "discussion_id": message.discussion_id,
            "user_address": message.user_address,
            "username": message.username,
            "message": message.message,
            "stance": message.stance,
            "timestamp": message.created_at.isoformat()
        }
    }

@app.get("/")
def read_root():
    return {"message": "Hello, World!"}

# Add a function to process juror responses
async def process_juror_responses(db, message_id: int, discussion_id: int):
    try:
        debate_info = get_debate(db, discussion_id)
        past_messages = get_chat_history(db, discussion_id)
        jurors = get_jurors(db, discussion_id)
        
        conv_history = ""
        for msg in past_messages[:-1]:
            user = get_user(db, msg.user_address)
            conv_history += f"{user.username}: {msg.message}\n"
        
        new_message = f"{past_messages[-1].username}: {past_messages[-1].message}"
        
        sides = []
        for idx, side in enumerate(debate_info.sides):
            sides.append(Side(id=str(idx), description=side))
        
        results = {}
        for juror_db in jurors:
            juror = Juror(persona=juror_db.persona)
            past_reasoning_list = get_juror_result(db, juror_db.juror_id, discussion_id)
            past_reasoning = past_reasoning_list[-1].reasoning if past_reasoning_list else ""
            previous_decision = past_reasoning_list[-1].result if past_reasoning_list else -1
            result, reasoning = juror.judge(topic=debate_info.topic, sides=sides, conv_history=conv_history, past_reasoning=past_reasoning, previous_decision=previous_decision, new_message=new_message)
            results[juror_db.juror_id] = {
                "result": result,
                "reasoning": reasoning
            }
            create_juror_result(
                db=db, 
                discussion_id=discussion_id, 
                latest_msg_id=message_id, 
                juror_id=juror_db.juror_id, 
                result=result, 
                reasoning=reasoning
            )
                
        db.commit()

        # Prepare juror response data for broadcast
        response_data = {
            "type": "juror_response",
            "data": {
                "message_id": message_id,
                "responses": results
            }
        }
        
        # Broadcast the juror responses
        await manager.broadcast_message(str(discussion_id), response_data)
        
    except Exception as e:
        logger.error(f"Error processing juror responses: {str(e)}")
        db.rollback()

@app.post("/msg")
async def post_msg(request: ChatMessage, background_tasks: BackgroundTasks):
    db = SessionLocal()
    try:
        logger.info(f"Received message request: {request}")
        
        new_message = create_chat_message(
            db=db,
            discussion_id=request.discussion_id,
            user_address=request.user_address,
            username=request.username,
            message=request.message,
            stance=request.stance
        )
        db.commit()
        
        # Immediately broadcast the message
        await manager.broadcast_message(str(request.discussion_id), wrap_message(new_message))
        
        # Process juror responses in the background
        background_tasks.add_task(
            process_juror_responses,
            db=SessionLocal(),  # Create a new db session for background task
            message_id=new_message.id,
            discussion_id=request.discussion_id
        )
        
        # Check message count and process debate if needed
        message_count = len(get_chat_history(db, request.discussion_id))
        if message_count >= 3:
            logger.info(f"Debate {request.discussion_id} has reached 3 messages, processing results...")
            
            # Process debate results in background
            background_tasks.add_task(
                process_debate_end,
                debate_id=str(request.discussion_id)
            )
            
            # Prepare debate end notification
            end_notification = {
                "type": "new_message",
                "data": {
                    "username": "Judge Agent",
                    "user_address": "",
                    "message": "Debate has reached 3 messages and will now be processed for final results.",
                    "timestamp": datetime.datetime.now().isoformat()
                }
            }
            await manager.broadcast_message(str(request.discussion_id), end_notification)
        
        return {"message_id": new_message.id, "status": "success"}
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating message: {str(e)}")
    finally:
        db.close()

async def process_debate_end(debate_id: str):
    """Process the debate end after 3 messages."""
    try:
        # Call the process_debate_result endpoint
        async with AsyncClient() as client:
            response = await client.post(
                f"http://localhost:8000/debate/{debate_id}/process_result"
            )
            
            print("response from process_debate_result: ", response)
            
            if response.status_code == 200:
                result = response.json()
                # Broadcast the results using new_message type
                await manager.broadcast_message(
                    debate_id,
                    {
                        "type": "new_message",
                        "data": {
                            "username": "Judge Agent",
                            "user_address": result.get("judge_address", ""),
                            "message": "✅ Final Results:\n" + json.dumps(result, indent=2),
                            "timestamp": datetime.datetime.now().isoformat()
                        }
                    }
                )
            else:
                logger.error(f"Error processing debate end: {response.text}")
                # Broadcast error using new_message type
                await manager.broadcast_message(
                    debate_id,
                    {
                        "type": "new_message",
                        "data": {
                            "username": "Judge Agent",
                            "user_address": "",
                            "message": f"❌ Error processing debate results:\n{response.text}",
                            "timestamp": datetime.datetime.now().isoformat()
                        }
                    }
                )
                
    except Exception as e:
        logger.error(f"Error in process_debate_end: {str(e)}")
        # Broadcast error using new_message type
        await manager.broadcast_message(
            debate_id,
            {
                "type": "new_message",
                "data": {
                    "username": "Judge Agent",
                    "user_address": "",
                    "message": f"❌ Error processing debate results:\n{str(e)}",
                    "timestamp": datetime.datetime.now().isoformat()
                }
            }
        )

@app.post("/juror_response/{message_id}")
async def get_juror_response(message_id: int, background_tasks: BackgroundTasks):
    db = SessionLocal()
    try:
        from backend.database.chat_message import ChatMessageDB
        
        message = db.query(ChatMessageDB).filter(ChatMessageDB.id == message_id).first()
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")
            
        debate_info = get_debate(db, message.discussion_id)
        past_messages = get_chat_history(db, message.discussion_id)
        jurors = get_jurors(db, message.discussion_id)
        
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
            result, reasoning = juror.judge(topic=debate_info.topic, sides=sides, conv_history=conv_history, previous_decision=message.stance)
            results[juror_db.juror_id] = {
                "result": result,
                "reasoning": reasoning
            }
            create_juror_result(
                db=db, 
                discussion_id=message.discussion_id, 
                latest_msg_id=message_id, 
                juror_id=juror_db.juror_id, 
                result=result, 
                reasoning=reasoning
            )
                
        db.commit()

        # Prepare response data for broadcast
        response_data = {
            "type": "juror_response",
            "data": {
                "message_id": message_id,
                "responses": results
            }
        }
        
        # Add broadcast task to background tasks
        background_tasks.add_task(
            manager.broadcast_message,
            str(message.discussion_id),
            response_data
        )
        
        return results
    except Exception as e:
        db.rollback()
        logger.error(f"Error getting juror response: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error getting juror response: {str(e)}")
    finally:
        db.close()

@app.get("/msg/{discussion_id}", response_model=List[ChatMessage])
def get_msg(discussion_id: int):
    db = SessionLocal()
    try:
        response = get_chat_history(db, discussion_id)
        messages = []
        for res in response:
            messages.append(ChatMessage(
                discussion_id=res.discussion_id,
                username=res.username,
                user_address=res.user_address,
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
            user_address=request.user_address
        )
        return new_user.to_dict()
    except Exception as e:
        logger.error(f"Error in post_user: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.get("/user/{user_address}")
def get_user_info(user_address: str):
    db = SessionLocal()
    try:
        user = get_user(db, user_address)
        if user:
            return user.to_dict()
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        logger.error(f"Error getting user info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@app.post("/debate")
def post_debate(request: Debate):
    db = SessionLocal()
    try:
        # Generate new discussion_id
        # latest_debate = db.query(DebateDB).order_by(DebateDB.discussion_id.desc()).first()
        # discussion_id = (latest_debate.discussion_id + 1) if latest_debate else 1
        
        # 检查是否已存在相同的 discussion_id
        if request.discussion_id:
            existing_debate = db.query(DebateDB).filter(DebateDB.discussion_id == request.discussion_id).first()
            if existing_debate:
                raise HTTPException(status_code=400, detail=f"Debate with discussion_id {request.discussion_id} already exists")
            discussion_id = request.discussion_id
        else:
            # 如果没有提供 discussion_id，则自动生成
            latest_debate = db.query(DebateDB).order_by(DebateDB.discussion_id.desc()).first()
            discussion_id = (latest_debate.discussion_id + 1) if latest_debate else 1
        
        # Set debate_id for the singleton manager
        debate_manager.debate_id = str(discussion_id)
        
        try:
            wallet_info = debate_manager.initialize_debate()
            logger.info(f"Debate wallets initialized: {wallet_info}")
        except Exception as e:
            logger.error(f"Error initializing debate wallets: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error initializing debate wallets: {str(e)}")
        
        # Create jurors
        juror_ids = []
        for idx, persona in enumerate(request.jurors):
            create_juror(db=db, discussion_id=discussion_id, juror_id=idx, persona=persona)
            juror_ids.append(idx)

        # Create debate
        try:
            new_debate = create_debate(
                db=db,
                discussion_id=discussion_id,
                topic=request.topic,
                sides=request.sides,
                juror_ids=juror_ids,
                funding=request.funding,
                action=request.action,
                creator_address=request.creator_address
            )
            db.commit()
            
            # Return complete debate information including wallet addresses
            return {
                "discussion_id": new_debate.discussion_id,
                "topic": new_debate.topic,
                "sides": request.sides,
                "action": new_debate.action,
                "funding": new_debate.funding,
                "jurors": request.jurors,
                "creator_address": new_debate.creator_address,
                "creator_username": request.creator_username,  # 添加创建者用户名
                "created_at": new_debate.created_at.isoformat(),  # 添加创建时间
                "privy_wallet_address": wallet_info['privy_wallet_address'],
                "privy_wallet_id": wallet_info['privy_wallet_id'],
                "cdp_wallet_address": wallet_info['cdp_wallet_address']
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
        logger.info(f"Fetching juror results for discussion_id: {discussion_id}")
        juror_results = get_all_juror_results(db, discussion_id)
        logger.info(f"Found {len(juror_results)} juror results")
        return juror_results
    except Exception as e:
        logger.error(f"Error getting juror results: {str(e)}")
        logger.error(f"Error type: {type(e)}")
        logger.error(f"Error traceback:", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error retrieving juror results: {str(e)}")
    finally:
        db.close()

@app.post("/generate_personas")
def generate_personas(request: GeneratePersonasRequest):
    """Generate a list of diverse juror personas"""
    try:
        topic = request.topic
        personas = generate_juror_persona(topic)
        return {"personas": personas}
    except Exception as e:
        logger.error(f"Error generating personas: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating juror personas")

@app.websocket("/ws/{debate_id}/{client_id}")
async def websocket_endpoint(websocket: WebSocket, debate_id: str, client_id: str):
    await manager.connect(websocket, debate_id, client_id)
    try:
        while True:
            # Keep the connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(debate_id, client_id)

@app.get("/debate/{debate_id}/funding_status")
async def check_debate_funding_status(debate_id: str):
    """Check the funding status of a debate's wallets."""
    db = SessionLocal()
    try:
        # Get debate information
        debate = get_debate(db, debate_id)
        if not debate:
            raise HTTPException(status_code=404, detail="Debate not found")
            
        # Set debate_id for the singleton manager
        debate_manager.debate_id = debate_id
        
        # Get wallet information
        wallet_info = get_debate_wallets(debate_id)
        if not wallet_info:
            raise HTTPException(status_code=404, detail="Wallet information not found")
            
        # Check CDP wallet funding
        cdp_funded, cdp_balance = debate_manager.check_funding_status(
            wallet_info['cdp_wallet_address'],
            0.0001  # Required CDP gas amount
        )
        
        # Check Privy wallet funding if required
        privy_funded = False
        privy_balance = 0
        if debate.funding > 0:
            privy_funded, privy_balance = debate_manager.check_funding_status(
                wallet_info['privy_wallet_address'],
                float(debate.funding)
            )
        else:
            privy_funded = True  # If no funding required, consider it funded
            
        return {
            "cdp_funded": cdp_funded,
            "privy_funded": privy_funded,
            "cdp_balance": cdp_balance,
            "privy_balance": privy_balance,
            "required_cdp_amount": 0.0001,
            "required_privy_amount": float(debate.funding),
            "message": (
                f"CDP Wallet: {cdp_balance:.6f} ETH (Required: 0.0001 ETH)\n" +
                (f"Privy Wallet: {privy_balance:.6f} ETH (Required: {debate.funding} ETH)"
                 if debate.funding > 0 else "No funding required for Privy wallet")
            )
        }
        
    except Exception as e:
        logger.error(f"Error checking funding status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error checking funding status: {str(e)}")
    finally:
        db.close()

@app.post("/debate/{debate_id}/process_result")
async def process_debate_result(debate_id: str):
    """Process the debate result and execute necessary actions based on voting outcome."""
    db = SessionLocal()
    try:
        # Get debate information
        debate = get_debate(db, debate_id)
        if not debate:
            raise HTTPException(status_code=404, detail="Debate not found")
            
        # Set debate_id for the singleton manager
        debate_manager.debate_id = debate_id
        
        # Get all juror results
        juror_results = get_all_juror_results(db, debate_id)
        if not juror_results:
            raise HTTPException(
                status_code=400, 
                detail="No juror results found. Ensure all jurors have voted."
            )
            
        # Get chat history
        chat_history = get_chat_history(db, debate_id)
        debate_history = "\n".join([
            f"{msg.username}: {msg.message}" 
            for msg in chat_history
        ])
 
        # Prepare voting results
        ai_votes = {}
        ai_reasoning = {}
        for juror_results_list in juror_results:
            # Get the latest result for each juror
            if juror_results_list:  # Check if there are any results for this juror
                latest_result = juror_results_list[-1]  # Get the most recent result
                if type(latest_result.result) != int:
                    raise HTTPException(status_code=400, detail="Juror result is not an integer")
                ai_votes[str(latest_result.juror_id)] = latest_result.result
                ai_reasoning[str(latest_result.juror_id)] = latest_result.reasoning
            
        # Process the result
        try:
            # Get wallet information for the debate
            wallet_info = get_debate_wallets(debate_id)
            if not wallet_info:
                raise HTTPException(status_code=404, detail="Wallet information not found")
            
            judge_address = wallet_info['cdp_wallet_address']
            
            # Create metadata for NFT
            metadata = {
                "name": f"Debate NFT {debate_id}",
                "description": "NFT representing a DAO debate result",
                "debate_id": debate_id,
                "debate_history": debate_history,
                "ai_votes": ai_votes,
                "ai_reasoning": ai_reasoning,
                "privy_wallet_id": wallet_info['privy_wallet_id'],
                "timestamp": str(datetime.datetime.now().isoformat())
            }
            
            
            
            # 1. Deploy NFT contract
            try:
                contract_address, deploy_response = debate_manager.deploy_nft(metadata)
                judge_message = create_chat_message(
                    db=db,
                    discussion_id=debate_id,
                    user_address=judge_address,
                    username="Judge Agent",
                    message=f"🔨 NFT Contract Deployed!\n{deploy_response}",
                    stance=None
                )
                db.commit()
                await manager.broadcast_message(debate_id, wrap_message(judge_message))
                
            except Exception as e:
                error_msg = f"Failed to deploy NFT contract: {str(e)}"
                logger.error(error_msg)
                await manager.broadcast_message(
                    debate_id,
                    {
                        "type": "new_message",
                        "data": {
                            "id": f"result-nft-deploy-error-{debate_id}",
                            "message": f"❌ {error_msg}",
                            "user_address": judge_address,
                            "username": "Judge Agent",
                            "timestamp": datetime.datetime.now().isoformat(),
                            "stance": None
                        }
                    }
                )
                raise
            
            # 2. Mint NFT
            try:
                mint_response = debate_manager.mint_nft(contract_address)
                judge_message = create_chat_message(
                    db=db,
                    discussion_id=debate_id,
                    user_address=judge_address,
                    username="Judge Agent",
                    message=f"🎨 NFT Minted Successfully!\n{mint_response}",
                    stance=None
                )
                await manager.broadcast_message(debate_id, wrap_message(judge_message))
            except Exception as e:
                error_msg = f"Failed to mint NFT: {str(e)}"
                logger.error(error_msg)
                await manager.broadcast_message(
                    debate_id,
                    {
                        "type": "new_message",
                        "data": {
                            "id": f"result-nft-mint-error-{debate_id}",
                            "message": f"❌ {error_msg}",
                            "user_address": judge_address,
                            "username": "Judge Agent",
                            "timestamp": datetime.datetime.now().isoformat(),
                            "stance": None
                        }
                    }
                )
                raise
            
            # 3. Execute action based on agent's evaluation
            
            # Format AI votes into a prompt
            votes_summary = []
            for juror_id, vote in ai_votes.items():
                votes_summary.append(f"Juror {juror_id}:\nVote: { debate.sides[vote] }")
            
            votes_text = "\n".join(votes_summary)
            action_prompt = f"""Here are the AI jurors' votes:
                            {votes_text}
                            This is the amount of funding currently in the Privy wallet:
                            {debate.funding}
                            This is the action prompt:
                            {debate.action}
                            Based on the votes and the action prompt, please execute the action if necessary."""

            
            try:
                action_result = debate_manager.execute_action(
                    action_prompt=action_prompt,
                    privy_wallet_id=wallet_info['privy_wallet_id']
                )
                judge_message = create_chat_message(
                    db=db,
                    discussion_id=debate_id,
                    user_address=judge_address,
                    username="Judge Agent",
                    message=f"⚡ Action Result:\n{action_result}",
                    stance=None
                )
                await manager.broadcast_message(debate_id, wrap_message(judge_message))
        
            except Exception as e:
                error_msg = f"Failed to execute action: {str(e)}"
                logger.error(error_msg)
                await manager.broadcast_message(
                    debate_id,
                    {
                        "type": "new_message",
                        "data": {
                            "id": f"result-action-error-{debate_id}",
                            "message": f"❌ {error_msg}",
                            "user_address": judge_address,
                            "username": "Judge Agent",
                            "timestamp": datetime.datetime.now().isoformat(),
                            "stance": None
                        }
                    }
                )
                raise
            
            # Final summary message
            judge_message = create_chat_message(
                db=db,
                discussion_id=debate_id,
                user_address=judge_address,
                username="Judge Agent",
                message="✅ Debate processing completed!\n\n"
            )
            await manager.broadcast_message(debate_id, wrap_message(judge_message))
            
            return {
                "success": True,
                "debate_id": debate_id,
                "nft_deployment": deploy_response,
                "nft_contract": contract_address,
                "nft_minting": mint_response,
                "action_execution": action_result,
                "voting_results": {
                    "total_votes": len(ai_votes),
                    "approval_count": sum(ai_votes.values()),
                    "votes": ai_votes,
                    "reasoning": ai_reasoning
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing debate result: {str(e)}")
            # Broadcast error message
            await manager.broadcast_message(
                debate_id,
                {
                    "type": "new_message",
                    "data": {
                        "username": "Judge Agent",
                        "user_address": "",
                        "message": f"❌ Error during debate processing:\n{str(e)}",
                        "timestamp": datetime.datetime.now().isoformat()
                    }
                }
            )
            raise HTTPException(
                status_code=500,
                detail=f"Error processing debate result: {str(e)}"
            )
            
    except Exception as e:
        logger.error(f"Error in process_debate_result: {str(e)}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        # Broadcast error message
        await manager.broadcast_message(
            debate_id,
            {
                "type": "new_message",
                "data": {
                    "username": "Judge Agent",
                    "user_address": "",
                    "message": f"❌ Error processing debate:\n{str(e)}",
                    "timestamp": datetime.datetime.now().isoformat()
                }
            }
        )
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
