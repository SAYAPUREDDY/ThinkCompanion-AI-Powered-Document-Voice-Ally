from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Message(BaseModel):
    role: str  # "User" or "AI"
    content: str

class ChatSession(BaseModel):
    session_id: str = Field(..., description="Unique identifier for the chat session")
    history: List[Message] = Field(default_factory=list, description="Chat history")
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow, description="Timestamp of creation")
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow, description="Timestamp of last update")
