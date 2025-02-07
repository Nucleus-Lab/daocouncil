from datetime import datetime
from typing import List
from sqlalchemy import Column, Integer, String, DateTime, BigInteger
from sqlalchemy.exc import IntegrityError
from . import Base, engine

# User model
class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255))
    user_address = Column(String(255), unique=True)
    debate_id = Column(BigInteger, nullable=True)  # 添加 debate_id 字段
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

# Database operations for user
def create_user(db, username: str, user_address: str, debate_id: int = None):
    try:
        # 检查用户是否已存在
        existing_user = get_user(db, user_address)
        if existing_user:
            # 如果用户存在，更新用户名和辩论ID
            existing_user.username = username
            existing_user.debate_id = debate_id
            existing_user.updated_at = datetime.utcnow()
            db.flush()
            return existing_user
        
        # 如果用户不存在，创建新用户
        new_user = UserDB(
            username=username,
            user_address=user_address,
            debate_id=debate_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(new_user)
        db.flush()
        return new_user
    except Exception as e:
        raise Exception(f"Error creating/updating user: {str(e)}")

def get_user(db, user_address: str) -> UserDB:
    return db.query(UserDB)\
        .filter(UserDB.user_address == user_address)\
        .first()

def get_debate_users(db, debate_id: int) -> List[UserDB]:
    return db.query(UserDB)\
        .filter(UserDB.debate_id == debate_id)\
        .all()

# 只创建不存在的表
Base.metadata.create_all(bind=engine)