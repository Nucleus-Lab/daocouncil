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

# Create single judge instance
judge_agent = JudgeAgent()

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
    """Chat with the judge agent for a specific debate."""
    try:
        logger.info(f"Processing chat request for debate {request.debate_id}")
        response = judge_agent.chat(request.debate_id, request.message)
        
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