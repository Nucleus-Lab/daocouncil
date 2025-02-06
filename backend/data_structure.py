from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
@dataclass
class ChatMessage:
    discussion_id: int
    user_address: str
    message: str
    username: Optional[str] = None
    timestamp: Optional[datetime] = None
    stance: Optional[str] = None

@dataclass
class User:
    username: str
    user_address: str
    debate_id: Optional[int] = None

@dataclass
class Debate:
    discussion_id: int
    topic: str
    sides: List[str]
    jurors: List[str]
    funding: float
    action: str
    creator_address: str
    
class Side(BaseModel):
    id: str
    description: str
