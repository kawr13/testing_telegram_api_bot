from enum import IntEnum, Enum
from pyrogram import Client
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Enum, update
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from datetime import datetime, timedelta, timezone
from icecream import ic
from tortoise import fields
from tortoise.models import Model
from config import Base, client
import enum


utc_tz = timezone.utc

class Status(enum.Enum):
    alive = "alive"
    dead = "dead"
    finished = "finished"


# db SQLAlchemy
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=lambda: datetime.utcnow().replace(tzinfo=utc_tz))
    status = Column(Enum(Status), default=Status.alive)
    status_updated_at = Column(DateTime, default=lambda: datetime.utcnow().replace(tzinfo=utc_tz))
    msg1_sent_at = Column(DateTime, nullable=True)
    msg2_sent_at = Column(DateTime, nullable=True)
    msg3_sent_at = Column(DateTime, nullable=True)