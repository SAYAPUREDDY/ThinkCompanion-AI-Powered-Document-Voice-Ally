from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
import shutil
from uuid import uuid4
import os

UPLOAD_DIR = Path("uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter()

@router.post("/upload-files/")
async def upload_files(session_id: str = None, files: list[UploadFile] = File(...)):
    if not session_id:
        session_id = str(uuid4())
    
    session_folder = UPLOAD_DIR / session_id
    session_folder.mkdir(parents=True, exist_ok=True)

    try:
        for file in files:
            file_path = session_folder / file.filename
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

        return JSONResponse(content={"message": "Files uploaded successfully.", "session_id": session_id}, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error uploading files: {str(e)}")

# @router.post(/upload_links)
# async def upload_links(session_id:str=none,links_url:str=None)