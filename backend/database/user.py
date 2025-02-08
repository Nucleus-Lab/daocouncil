from datetime import datetime
from typing import List
from sqlalchemy import Column, Integer, String, DateTime, text
from sqlalchemy.exc import IntegrityError
from . import Base, engine

# User model
class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255))
    user_address = Column(String(255), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "username": self.username,
            "user_address": self.user_address,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

# Database operations for user
def create_user(db, username: str, user_address: str):
    try:
        # 尝试直接创建新用户
        new_user = UserDB(
            username=username,
            user_address=user_address,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(new_user)
        db.commit()
        return new_user
    except IntegrityError:
        # 如果出现唯一约束冲突，说明用户已存在，更新用户名
        db.rollback()
        existing_user = db.query(UserDB).filter(UserDB.user_address == user_address).first()
        if existing_user:
            existing_user.username = username
            existing_user.updated_at = datetime.utcnow()
            db.commit()
            return existing_user
        raise Exception("Failed to create or update user")

def get_user(db, user_address: str) -> UserDB:
    return db.query(UserDB)\
        .filter(UserDB.user_address == user_address)\
        .first()

# 创建不存在的表
Base.metadata.create_all(bind=engine)