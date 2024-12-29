import os
import motor.motor_asyncio
from urllib import parse
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# print(f"Connecting the MongoDB database with username = {DB_USERNAME} and password = {DB_PASSWORD}")

# Database URL ( have to get via a env variable )
MONGO_DETAILS = f"mongodb+srv://{DB_USERNAME}:{DB_PASSWORD}@cluster0.fahmd.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)

database = client.ThinkCompanion

# async def test_mongo_connection():
#     try:
#         await client.admin.command("ping")
#         print("MongoDB connection successful.")
#     except Exception as e:
#         print(f"MongoDB connection failed: {e}")

# import asyncio
# asyncio.run(test_mongo_connection())

