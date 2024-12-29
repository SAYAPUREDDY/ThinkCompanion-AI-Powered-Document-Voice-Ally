from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
import json
from functions.update_chat import update_chat_history
from functions.rag_functions import rag_pipeline, process_uploaded_file
from database.connection import database
from utils.chats_utils import get_chat_session

chat_collection = database.get_collection("chats")

CHAT_DIR = Path("chats")
UPLOAD_DIR = Path("uploads")
CHAT_DIR.mkdir(parents=True, exist_ok=True)

router = APIRouter()

@router.post("/save-chat/")
async def save_chat(session_id: str):
    try:
        # Fetch chat session from MongoDB
        chat_session = await get_chat_session(chat_collection, session_id)
        if not chat_session:
            raise HTTPException(status_code=404, detail="Chat session not found.")

        # File-based backup (optional, if needed)
        file_path = CHAT_DIR / f"chat_history_{session_id}.json"
        with open(file_path, "w") as file:
            json.dump(chat_session["history"], file, indent=4)

        return JSONResponse(content={"message": f"Chat saved to MongoDB and optionally to {file_path}."}, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error saving chat: {str(e)}")

@router.get("/get-chat/")
async def get_chat_history(session_id: str):
    try:
        # Retrieve chat history from MongoDB
        chat_session = await get_chat_session(chat_collection, session_id)
        if not chat_session:
            raise HTTPException(status_code=404, detail="Chat session not found.")

        return JSONResponse(content={"chat_history": chat_session["history"]}, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error retrieving chat history: {str(e)}")
