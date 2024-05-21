from tortoise import Tortoise
from typing import Callable
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Enum, update
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from datetime import datetime, timedelta
from pyrogram import Client
from dotenv import load_dotenv
import os

load_dotenv()

api_id: int = int(os.getenv("API_ID"))
api_hash: str = os.getenv("API_HASH")
Base = declarative_base()
client: Client = Client(name="my_account", api_id=api_id, api_hash=api_hash)

DATABASE_URL: str = os.getenv("DATABASE_URL")

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def disconnect_db():
    await Tortoise.close_connections()