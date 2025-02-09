import os
from datetime import datetime
from typing import Optional
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Base = declarative_base()

class PrivyWalletDB(Base):
    __tablename__ = "privy_wallets"

    id = Column(Integer, primary_key=True, index=True)
    debate_id = Column(Integer, index=True)
    cdp_wallet_address = Column(String)
    privy_wallet_address = Column(String)
    privy_wallet_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

def create_privy_wallet(db, debate_id: int, cdp_wallet_address: str, privy_wallet_address: str, privy_wallet_id: str):
    new_wallet = PrivyWalletDB(
        debate_id=debate_id,
        cdp_wallet_address=cdp_wallet_address,
        privy_wallet_address=privy_wallet_address,
        privy_wallet_id=privy_wallet_id
    )
    db.add(new_wallet)
    db.commit()
    db.refresh(new_wallet)
    return new_wallet

def get_privy_wallet(db, debate_id: int) -> Optional[PrivyWalletDB]:
    return db.query(PrivyWalletDB)\
        .filter(PrivyWalletDB.debate_id == debate_id)\
        .first()

Base.metadata.create_all(bind=engine)