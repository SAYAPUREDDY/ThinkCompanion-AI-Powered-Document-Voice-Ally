from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
import json
import shutil
from uuid import uuid4
import os
import uvicorn

from functions.rag_functions import rag_pipeline, get_session_history, process_uploaded_file,save_chat_to_file
from functions.loader_mapping import loader_mapping
from functions.update_chat import update_chat_history
from functions.mime_detect import get_mime_types

app = FastAPI()

# Directory where uploaded files will be saved
UPLOAD_DIR = Path("uploads")
# Directory to store the chats
CHAT_DIR = Path("chats")  

# Ensure the necessary directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CHAT_DIR, exist_ok=True)

@app.post("/upload-files/")
async def upload_files(files: list[UploadFile] = File(...)):
    """Endpoint to upload multiple files"""
    # Generate a unique session ID for the user
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


@app.post("/chat/")
async def chat_with_bot(session_id: str, user_input: str):
    """Endpoint to interact with the chatbot"""
    try:
        session_folder = UPLOAD_DIR / session_id
        if not session_folder.exists():
            raise HTTPException(status_code=404, detail="Session not found.")
        
        retriever = None
        for file in session_folder.iterdir():
                    mime_type=get_mime_types(session_folder)
                    print(mime_type)
                    file_content = loader_mapping(mime_type, file)
                    retriever = process_uploaded_file(file_content) 

        if not retriever:
            raise HTTPException(status_code=400, detail="No valid files processed for retrieval.")

        response = rag_pipeline(retriever, session_id=session_id, user_input=user_input)

        return JSONResponse(content={"response": response}, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing the chat: {str(e)}")


@app.post("/save-chat/")
async def save_chat(session_id: str):
    """Endpoint to save the chat history for a session"""
    try:
        session_folder = UPLOAD_DIR / session_id
        if not session_folder.exists():
            raise HTTPException(status_code=404, detail="Session not found.")
        
        # Save the chat history to a file
        file_path = f"chat_history_{session_id}.json"
        save_chat_to_file(session_id, file_path)

        return JSONResponse(content={"message": f"Chat saved to {file_path}."}, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error saving chat: {str(e)}")


@app.get("/sessions/")
async def list_sessions():
    """Endpoint to list all active sessions"""
    try:
        sessions = [f.name for f in UPLOAD_DIR.iterdir() if f.is_dir()]
        return JSONResponse(content={"active_sessions": sessions}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error listing sessions: {str(e)}")


@app.get("/chats/")
async def list_chats():
    """Endpoint to list all saved chats"""
    try:
        chats = [f.name for f in CHAT_DIR.iterdir() if f.is_file()]
        return JSONResponse(content={"saved_chats": chats}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error listing chats: {str(e)}")


@app.get("/get-chat/")
async def get_chat_history(session_id: str):
    """Endpoint to retrieve the chat history for a session"""
    try:
        file_path = CHAT_DIR / f"chat_history_{session_id}.json"
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Chat history not found.")

        with open(file_path, "r") as file:
            chat_history = file.read()

        return JSONResponse(content={"chat_history": chat_history}, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error retrieving chat history: {str(e)}")
    
@app.post("/resume-chat/")
async def resume_chat(session_id: str, user_input: str):
    """Endpoint to resume the chat from a previous session"""
    try:
        # Validate session folder and check if chat history exists
        session_folder = UPLOAD_DIR / session_id
        if not session_folder.exists():
            raise HTTPException(status_code=404, detail="Session not found.")
        
        chat_history_file = CHAT_DIR / f"chat_history_{session_id}.json"
        if not chat_history_file.exists():
            raise HTTPException(status_code=404, detail="No previous chat history found for this session.")

        # Load the previous chat history from file
        with open(chat_history_file, "r") as file:
            chat_history = json.load(file)

        # Append the new user input to the chat history
        chat_history.append({"role": "User", "content": user_input})

        # Process the new input to generate a response
        retriever = None
        for file in session_folder.iterdir():
            mime_type=get_mime_types(session_folder)
            file_content = loader_mapping(mime_type, file)
            retriever = process_uploaded_file(file_content)

        if not retriever:
            raise HTTPException(status_code=400, detail="No valid files processed for retrieval.")

        # Get the chatbot response based on user input and retriever
        response = rag_pipeline(retriever, session_id=session_id, user_input=user_input)

        # Append the AI's response to chat history
        chat_history.append({"role": "AI", "content": response})

        # Update the chat history by calling the new update function
        update_chat_history(session_id, user_input, response)

        return JSONResponse(content={"response": response, "chat_history": chat_history}, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error resuming chat: {str(e)}")



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)






