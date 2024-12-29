from fastapi import FastAPI
from pathlib import Path
import os
import uvicorn
from routes.routes_mapping import include_routes

# Directories for file uploads and chat history
UPLOAD_DIR = Path("uploads")
CHAT_DIR = Path("chats")

# Ensure the necessary directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(CHAT_DIR, exist_ok=True)

# Initialize FastAPI application
app = FastAPI(title="ThinkCompanion", description="API for file uploads and chatbot interaction", version="1.0.0")

# Include routes using the mapping function
include_routes(app)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the ThinkCompanion, Your Intelligent Documemt Ally!"}

# Run the application with Uvicorn
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)











