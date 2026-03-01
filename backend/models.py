"""Таблицы базы данных."""
import uuid
import random
from datetime import datetime
from sqlalchemy import (
    Column, String, BigInteger, Integer, Float,
    Boolean, DateTime, ForeignKey, Text
)
from database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String, nullable=True)
    role = Column(String, default="insider")
    balance_ton = Column(Float, default=0.0)
    balance_gram = Column(Float, default=0.0)
    balance_not = Column(Float, default=0.0)
    withdrawn_ton = Column(Float, default=0.0)
    withdrawn_gram = Column(Float, default=0.0)
    withdrawn_not = Column(Float, default=0.0)
    ton_wallet = Column(String, nullable=True)
    views_since_captcha = Column(Integer, default=0)
    next_captcha_at = Column(Integer, default=lambda: random.randint(3, 15))
    referrer_id = Column(String, nullable=True)
    referral_code = Column(String, unique=True, default=lambda: uuid.uuid4().hex[:8])
    created_at = Column(DateTime, default=datetime.utcnow)


class Campaign(Base):
    __tablename__ = "campaigns"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    creator_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    media_url = Column(String, nullable=True)
    media_type = Column(String, default="text")
    target_link = Column(String, nullable=True)
    currency = Column(String, default="TON")
    status = Column(String, default="active")
    total_views = Column(Integer, nullable=False)
    delivered_views = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class AdView(Base):
    __tablename__ = "ad_views"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    campaign_id = Column(String, ForeignKey("campaigns.id"), nullable=False)
    currency = Column(String, default="TON")
    amount = Column(Float, default=0.1)
    viewed_at = Column(DateTime, default=datetime.utcnow)


class Feedback(Base):
    __tablename__ = "feedbacks"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id = Column(String, ForeignKey("campaigns.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    liked = Column(Boolean, nullable=False)
    comment = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Withdrawal(Base):
    __tablename__ = "withdrawals"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    currency = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    fee = Column(Float, default=0.3)
    net_amount = Column(Float, nullable=False)
    to_wallet = Column(String, nullable=False)
    status = Column(String, default="pending")
    tx_hash = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)