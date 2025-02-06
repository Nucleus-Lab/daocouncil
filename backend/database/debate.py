import json
from datetime import datetime
from typing import List
from sqlalchemy import Column, BigInteger, Integer, String, DateTime, Text, Float, ARRAY
from . import Base, engine

# Debate model
class DebateDB(Base):
    __tablename__ = "debates"

    id = Column(Integer, primary_key=True, index=True)
    discussion_id = Column(BigInteger, index=True, unique=True)
    topic = Column(Text)  # 使用 Text 而不是 String，以支持更长的内容
    sides = Column(ARRAY(String))  # Changed to ARRAY type
    juror_ids = Column(ARRAY(String))  # Changed to ARRAY type
    funding = Column(Float(precision=18, asdecimal=True))  # 使用高精度浮点数
    action = Column(Text)  # 使用 Text 而不是 String
    creator_address = Column(String(255))  # 指定长度的 String
    created_at = Column(DateTime, default=datetime.utcnow)


# Database operations for debate
def create_debate(db, discussion_id: int, topic: str, sides: List[str], juror_ids: List[int], funding: float, action: str, creator_address: str):
    try:
        new_debate = DebateDB(
            discussion_id=discussion_id,
            topic=topic,
            sides=sides,  # No need to convert to JSON
            juror_ids=juror_ids,  # No need to convert to JSON
            funding=funding,
            action=action,
            creator_address=creator_address,
            created_at=datetime.utcnow()
        )
        db.add(new_debate)
        db.flush()  # 检查约束条件
        return new_debate
    except Exception as e:
        raise Exception(f"Error creating debate: {str(e)}")

def get_debate(db, discussion_id: int) -> DebateDB:
    debate = db.query(DebateDB).filter(DebateDB.discussion_id == discussion_id).first()
    return debate  # No need to convert JSON strings back to lists

# 只创建不存在的表
Base.metadata.create_all(bind=engine)