from dataclasses import dataclass
from datetime import datetime


@dataclass
class ChatMessage:
    discussion_id: int
    username: str
    user_address: str
    message: str
    timestamp: datetime