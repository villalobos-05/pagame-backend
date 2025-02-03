from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()


# Dependency to get the database
async def get_db():
    client = AsyncIOMotorClient(
        os.getenv("MONGO_URI")
    )  # Create a new client for each request
    db = client[os.getenv("MAIN_DB")]  # Get the main database
    return db
