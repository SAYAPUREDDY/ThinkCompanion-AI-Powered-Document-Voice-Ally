from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path

UPLOAD_DIR = Path("uploads")
CHAT_DIR = Path("chats")

router = APIRouter()

@router.get("/sessions/")
async def list_sessions():
    try:
        sessions = [f.name for f in UPLOAD_DIR.iterdir() if f.is_dir()]
        return JSONResponse(content={"active_sessions": sessions}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error listing sessions: {str(e)}")
