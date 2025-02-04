from datetime import datetime
from typing import Dict, List, Optional
from .db_config import Database
from bson import ObjectId

class PatientOperations:
    @staticmethod
    async def create_patient(patient_data: Dict) -> str:
        """Create a new patient record"""
        patient_data["created_at"] = datetime.utcnow()
        patient_data["updated_at"] = datetime.utcnow()
        result = await Database.db.patients.insert_one(patient_data)
        return str(result.inserted_id)

    @staticmethod
    async def get_patient(patient_id: str) -> Optional[Dict]:
        """Get patient by ID"""
        return await Database.db.patients.find_one({"patient_id": patient_id})

    @staticmethod
    async def update_patient(patient_id: str, update_data: Dict) -> bool:
        """Update patient information"""
        update_data["updated_at"] = datetime.utcnow()
        result = await Database.db.patients.update_one(
            {"patient_id": patient_id},
            {"$set": update_data}
        )
        return result.modified_count > 0

class ImageUploadOperations:
    @staticmethod
    async def create_upload(upload_data: Dict) -> str:
        """Create new image upload record"""
        upload_data["upload_time"] = datetime.utcnow()
        upload_data["status"] = "pending"
        result = await Database.db.image_uploads.insert_one(upload_data)
        return str(result.inserted_id)

    @staticmethod
    async def get_recent_uploads(limit: int = 10) -> List[Dict]:
        """Get recent image uploads"""
        cursor = Database.db.image_uploads.find().sort("upload_time", -1).limit(limit)
        return await cursor.to_list(length=limit)

    @staticmethod
    async def update_analysis_result(upload_id: str, analysis_result: Dict) -> bool:
        """Update analysis result for an upload"""
        result = await Database.db.image_uploads.update_one(
            {"_id": ObjectId(upload_id)},
            {
                "$set": {
                    "analysis_result": analysis_result,
                    "status": "analyzed"
                }
            }
        )
        return result.modified_count > 0

class TrainingMetricsOperations:
    @staticmethod
    async def save_metrics(metrics_data: Dict) -> str:
        """Save training metrics"""
        metrics_data["timestamp"] = datetime.utcnow()
        result = await Database.db.training_metrics.insert_one(metrics_data)
        return str(result.inserted_id)

    @staticmethod
    async def get_latest_metrics(client_id: str) -> Optional[Dict]:
        """Get latest metrics for a client"""
        return await Database.db.training_metrics.find_one(
            {"client_id": client_id},
            sort=[("timestamp", -1)]
        )

    @staticmethod
    async def get_round_metrics(round_num: int) -> List[Dict]:
        """Get all metrics for a specific round"""
        cursor = Database.db.training_metrics.find({"round": round_num})
        return await cursor.to_list(length=100)

class GlobalModelOperations:
    @staticmethod
    async def save_model(model_data: Dict) -> str:
        """Save global model information"""
        model_data["created_at"] = datetime.utcnow()
        result = await Database.db.global_models.insert_one(model_data)
        return str(result.inserted_id)

    @staticmethod
    async def get_latest_model() -> Optional[Dict]:
        """Get latest global model"""
        return await Database.db.global_models.find_one(
            sort=[("round", -1)]
        )

    @staticmethod
    async def get_model_by_round(round_num: int) -> Optional[Dict]:
        """Get global model for specific round"""
        return await Database.db.global_models.find_one({"round": round_num})

class MetricsAggregator:
    @staticmethod
    async def get_dashboard_metrics() -> Dict:
        """Get aggregated metrics for dashboard"""
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "total_uploads": {"$sum": 1},
                    "analyses_completed": {
                        "$sum": {"$cond": [{"$eq": ["$status", "analyzed"]}, 1, 0]}
                    }
                }
            }
        ]
        
        result = await Database.db.image_uploads.aggregate(pipeline).to_list(length=1)
        
        if not result:
            return {
                "total_uploads": 0,
                "analyses_completed": 0,
                "accuracy_rate": 0
            }
            
        metrics = result[0]
        
        # Calculate accuracy rate from training metrics
        accuracy_pipeline = [
            {
                "$group": {
                    "_id": None,
                    "avg_accuracy": {"$avg": "$accuracy"}
                }
            }
        ]
        
        accuracy_result = await Database.db.training_metrics.aggregate(accuracy_pipeline).to_list(length=1)
        accuracy_rate = accuracy_result[0]["avg_accuracy"] if accuracy_result else 0
        
        return {
            "total_uploads": metrics["total_uploads"],
            "analyses_completed": metrics["analyses_completed"],
            "accuracy_rate": round(accuracy_rate, 2)
        }