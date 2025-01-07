from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional
import motor.motor_asyncio
import os
import json
from database.connection import database
from models.users import user_signup
from bson.objectid import ObjectId

user_collection = database.Users


class User_database:

    def __init__(self):
        pass
      
    async def get_user_from_email(email: str) -> dict:
        user = await user_collection.find_one({"email": email})
        if user:
            return await User_database.users_to_dict(user, with_password=True)
        else:
            return "RecordNotFound"
        
    async def users_to_dict(user, with_password) -> dict:
    # print(user["_id"])
        result = {
            "id": str(user["_id"]),
            "first_name": str(user["first_name"]),
            "last_name": str(user["last_name"]),
            "email": str(user["email"]),
            "verified": int(user["verified"]),
            "verification_code": str(user["verification_code"])
        }

        if with_password:
            result.update({"password": user["password"]})

        if "reset_token" in user:
            result.update({"reset_token": str(user["reset_token"])})
        else:
            result.update({"reset_token": "chums"})  # Handle the case where reset_token doesn't exist

        return result
    
    async def add_user(self,user_data:dict) -> dict:
        user = await user_collection.insert_one(user_data)
        new_user = await user_collection.find_one({"_id": user.inserted_id})
        return await User_database.users_to_dict(new_user, False)
    
    async def update_user(user_id: str, user_data: dict):
        result = await user_collection.update_one({"_id": ObjectId(user_id)}, {"$set": user_data})
        return result.modified_count