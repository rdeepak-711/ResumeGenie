import motor.motor_asyncio
from config import MONGODB_URI

client = None
db = None

async def get_database():
    global client, db

    if client is None:
        client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)
        db = client["resumegenie"]
    return db

async def get_resume_collection():
    db = await get_database()
    return db["resume"]

async def get_user_collection():
    db = await get_database()
    return db["user"]