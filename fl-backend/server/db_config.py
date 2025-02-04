from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "medai_assist")

class Database:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorClient] = None

    @classmethod
    async def connect_db(cls):
        cls.client = AsyncIOMotorClient(MONGODB_URL)
        cls.db = cls.client[DATABASE_NAME]
        print("Connected to MongoDB")

    @classmethod
    async def close_db(cls):
        if cls.client:
            cls.client.close()
            print("MongoDB connection closed")

# Collections
async def init_collections():
    """Initialize MongoDB collections with indexes"""
    db = Database.db
    
    # Patients collection
    await db.patients.create_index("patient_id", unique=True)
    
    # Image uploads collection
    await db.image_uploads.create_index("patient_id")
    await db.image_uploads.create_index("upload_time")
    
    # Training metrics collection
    await db.training_metrics.create_index([("round", 1), ("client_id", 1)])
    await db.training_metrics.create_index("timestamp")
    
    # Global models collection
    await db.global_models.create_index("round", unique=True)

# MongoDB schemas (for reference)
patient_schema = {
    "patient_id": str,
    "name": str,
    "email": str,
    "created_at": datetime,
    "updated_at": datetime
}

image_upload_schema = {
    "patient_id": str,
    "image_path": str,
    "image_type": str,
    "upload_time": datetime,
    "status": str,
    "analysis_result": dict,
    "metadata": dict
}

training_metrics_schema = {
    "round": int,
    "client_id": str,
    "accuracy": float,
    "loss": float,
    "timestamp": datetime,
    "metrics": dict
}

global_model_schema = {
    "round": int,
    "model_path": str,
    "metrics": dict,
    "created_at": datetime
}