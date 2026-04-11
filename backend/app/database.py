from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings
from loguru import logger

client: AsyncIOMotorClient = None
database: AsyncIOMotorDatabase = None

async def connect_to_mongo():
    """Create database connection"""
    global client, database
    try:
        client=AsyncIOMotorClient(
            settings.MONGO_URL,
            serverSelectionTimeoutMS=30000 , #30 seconds timeout
            ConnectTimeoutMS=30000,
            socketTimeoutMS=30000,
        )
        database=client[settings.DB_NAME]
        #test connection

        await client.admin.command('ping')
        logger.info(f"Connected to MongoDB: { settings.DB_NAME}")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB : { str(e)}")
        raise     

async def close_mongo_connection():
    """Close database connection"""
    global client
    if client:
        client.close()
        logger.info("MongoDB Connection closed")    

def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    return database
