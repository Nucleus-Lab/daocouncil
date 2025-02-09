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
class GeneratePersonasRequest:
    topic: str

@dataclass
class User:
    username: str
    user_address: str

@dataclass
class PrivyWalletRequest:
    debate_id: int
    cdp_wallet_address: str
    privy_wallet_address: str
    privy_wallet_id: str

class Side(BaseModel):
    id: str
    description: str

class Debate(BaseModel):
    discussion_id: Optional[int] = None
    topic: str
    sides: List[str]
    jurors: List[str]
    funding: float
    action: str
    creator_address: str
    creator_username: str
