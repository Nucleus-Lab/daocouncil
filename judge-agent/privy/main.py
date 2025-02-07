import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging
from judge import JudgeAgent
import uvicorn

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Judge Agent API",
    description="API for interacting with the DAO Judge Agent",
    version="1.0.0"
)

# Store agent instances
agent_instances = {}

class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    debate_id: str
    message: str

class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    debate_id: str
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat with the judge agent for a specific debate.
    
    If the agent doesn't exist for the debate, it will be created.
    """
    try:
        # Get or create agent instance
        if request.debate_id not in agent_instances:            
            logger.info(f"Creating new agent for debate: {request.debate_id}")
            agent_instances[request.debate_id] = JudgeAgent(
                debate_id=request.debate_id
            )
        
        # Get agent instance
        agent = agent_instances[request.debate_id]
        
        # Process message through agent
        logger.info(f"Processing message for debate {request.debate_id}")
        response = agent.chat(request.message)
        
        return ChatResponse(
            debate_id=request.debate_id,
            response=response
        )
        
    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat request: {str(e)}"
        )

if __name__ == "__main__":
    # Load environment variables
    port = int(os.getenv("PORT", "8000"))
    
    # Run the FastAPI application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True  # Enable auto-reload during development
    ) 