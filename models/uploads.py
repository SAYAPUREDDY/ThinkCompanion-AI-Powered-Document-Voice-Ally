from pydantic import BaseModel
from datetime import datetime

class ExtractedTexts(BaseModel):
    session_id: str
    filename: str
    file_path: str
    content: str  # Store a preview of the file content
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()  # Track when the metadata was last updated
