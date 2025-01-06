from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional
import motor.motor_asyncio
import os
from dotenv import load_dotenv
import json
from database.connection import database

chat_collection = database.get_collection("chats")


async def create_chat_session(chat_collection, session_id: str) -> dict:
    """Create a new chat session in MongoDB."""
    chat_data = {
        "session_id": session_id,
        "history": [],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    await chat_collection.insert_one(chat_data)
    return chat_data

async def get_chat_session(chat_collection, session_id: str) -> Optional[dict]:
    """Retrieve a chat session by its session_id."""
    return await chat_collection.find_one({"session_id": session_id})

async def update_chat_session(chat_collection, session_id: str, user_input: dict, ai_response: dict):
    """Update an existing chat session with a new interaction."""
    await chat_collection.update_one(
        {"session_id": session_id},
        {
            "$push": {"history": {"$each": [user_input, ai_response]}},
            "$set": {"updated_at": datetime.utcnow()},
        }
    )
