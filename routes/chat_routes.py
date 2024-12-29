from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
import json
from functions.rag_functions import rag_pipeline, process_uploaded_file
# from functions.loader_mapping import loader_mapping
# from functions.mime_detect import get_mime_type
from functions.update_chat import update_chat_history
from utils.chats_utils import get_chat_session,create_chat_session,update_chat_session
from functions.multiple_file_processor import process_files
# from utils.extracted_texts import create_upload_record 
from langchain_core.documents import Document
from database.connection import database

chat_collection = database.get_collection('chats')
# extracted_texts_collection = database.get_collection("extracted_texts")

UPLOAD_DIR = Path("uploads")
CHAT_DIR = Path("chats")

router = APIRouter()

@router.post("/chat/")
async def chat_with_bot(session_id: str, user_input: str):
    try:
        # Get or create session
        chat_session = await get_chat_session(chat_collection, session_id)
        if not chat_session:
            chat_session = await create_chat_session(chat_collection, session_id)

        session_folder = UPLOAD_DIR / session_id
        if not session_folder.exists():
            raise HTTPException(status_code=404, detail="Session not found.")

        retriever = None
        file_content = await process_files(session_id)
        # print("file content is okayy")
        retriever = process_uploaded_file(file_content) 
        # print("retriever is okayy")

        if not retriever:
            raise HTTPException(status_code=400, detail="No valid files processed for retrieval.")

        response = rag_pipeline(retriever, session_id=session_id, user_input=user_input)
        
        # Append messages to session
        user_message = {"role": "User", "content": user_input}
        ai_message = {"role": "AI", "content": response}
        await update_chat_session(chat_collection, session_id, user_message, ai_message)

        return JSONResponse(content={"response": response, "chat_history": chat_session["history"]}, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing chat: {str(e)}")


@router.post("/resume-chat/")
async def resume_chat(session_id: str, user_input: str):
    try:
        # Retrieve chat session
        chat_session = await get_chat_session(chat_collection, session_id)
        if not chat_session:
            raise HTTPException(status_code=404, detail="Chat session not found.")
        
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
        file_content = process_files(session_id)
        retriever = process_uploaded_file(file_content)

        if not retriever:
            raise HTTPException(status_code=400, detail="No valid files processed for retrieval.")


        # Process input and generate response
        response = rag_pipeline(retriever, session_id=session_id, user_input=user_input)

        # Update the chat history in the local files
        chat_history.append({"role": "AI", "content": response})
        update_chat_history(session_id, user_input, response)

        # Append messages to session
        user_message = {"role": "User", "content": user_input}
        ai_message = {"role": "AI", "content": response}
        # updates the chats in database
        await update_chat_session(chat_collection, session_id, user_message, ai_message)

        return JSONResponse(content={"response": response, "chat_history": chat_session["history"]}, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error resuming chat: {str(e)}")
