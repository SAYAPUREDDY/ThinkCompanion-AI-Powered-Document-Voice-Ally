from pydantic import BaseModel
from datetime import datetime

from typing import Optional
from pydantic import BaseModel, Field

# Database structure for user collection
class schema(BaseModel):
    first_name: str = Field(...)
    last_name: str = Field(...)
    email: str = Field(...)
    password: str = Field(...)

    class Config:
        json_schema_extra = {
            "example": {
                "first_name": "John",
                "last_name": "Doe",
                "email": "hello@test.com",
                "password": "testing_password",
            }
        }


# Login request payload structure
class user_login(BaseModel):
    email: str
    password: str

    class Config:
        json_schema_extra = {
            "example": {
                "email": "hello@test.com",
                "password": "testing_password",
            }
        }

# Signup request payload structure
class user_signup(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str
    verified:int
    verification_code:str
    class Config:
        json_schema_extra = {
            "example": {
                "first_name": "John",
                "last_name": "Doe",
                "email": "hello@test.com",
                "password": "testing_password",
                "verified":0,
                "verification_code":"string"
            }
        }

# Payload structure for requesting a password reset
class ForgotPassword(BaseModel):
    email: str
    reset_token: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "email": "hello@test.com",
                "reset_token": "example_reset_token"
            }
        }
        
        
        
# Update User payload structure
class update_user(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "first_name": "John",
                "last_name": "Doe",
            }
        }

class TokenModel(BaseModel):
    token: str

    
    