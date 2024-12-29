from datetime import datetime
from typing import Optional, List
from database.connection import database
from langchain_core.documents import Document

# Define the collection for uploads
extracted_texts_collection = database.get_collection("extracted_texts")

async def upsert_upload_record(
    extracted_texts_collection, session_id: str, content: list
):
    """Create or update a file upload record in MongoDB."""
    existing_record = await extracted_texts_collection.find_one({"session_id": session_id})
    
    if existing_record:
        # Update the existing record
        update_query = {
            "$set": {
                "content": content,
                "updated_at": datetime.utcnow(),
            }
        }
        await extracted_texts_collection.update_one(
            {"session_id": session_id}, update_query
        )
    else:
        # Insert a new record
        upload_data = {
            "session_id": session_id,
            "content": content,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        await extracted_texts_collection.insert_one(upload_data)

async def get_upload_records_by_session(extracted_texts_collection, session_id: str) -> List[dict]:
    """Retrieve all upload records for a specific session."""
    cursor = extracted_texts_collection.find({"session_id": session_id})
    return await cursor.to_list(length=None)

async def get_upload_record(extracted_texts_collection, session_id: str, filename: str) -> dict:
    """Retrieve a specific upload record by session_id and filename."""
    return await extracted_texts_collection.find_one({"session_id": session_id, "filename": filename})

async def update_upload_record(
    extracted_texts_collection, session_id: str, filename: str, updated_content: str = None
):
    """Update an existing file upload record in MongoDB."""
    update_query = {
        "$set": {
            "updated_at": datetime.utcnow(),
        }
    }
    if updated_content:
        update_query["$set"]["content_preview"] = updated_content[:500]

    await extracted_texts_collection.update_one(
        {"session_id": session_id, "filename": filename},
        update_query,
    )

async def delete_upload_record(extracted_texts_collection, session_id: str, filename: str):
    """Delete a specific upload record."""
    await extracted_texts_collection.delete_one({"session_id": session_id, "filename": filename})

async def delete_all_uploads_by_session(extracted_texts_collection, session_id: str):
    """Delete all upload records for a specific session."""
    await extracted_texts_collection.delete_many({"session_id": session_id})
