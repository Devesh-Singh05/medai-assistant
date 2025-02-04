import torch
import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from motor.motor_asyncio import AsyncIOMotorClient
from .db_operations import (
    GlobalModelOperations,
    TrainingMetricsOperations,
    MetricsAggregator,
    ImageUploadOperations
)
from .model import MedAIModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FederatedServer:
    def __init__(
        self,
        min_clients: int = 3,
        checkpoint_dir: str = "checkpoints",
        aggregation_threshold: float = 0.8
    ):
        self.min_clients = min_clients
        self.checkpoint_dir = Path(checkpoint_dir)
        self.checkpoint_dir.mkdir(exist_ok=True)
        self.aggregation_threshold = aggregation_threshold
        
        # Initialize model and training state
        self.model = MedAIModel()
        self.current_round = 0
        self.client_updates = {}
        self.training_in_progress = False
        
        # Load latest checkpoint if exists
        self._load_latest_checkpoint()

    async def _load_latest_checkpoint(self):
        """Load the latest model checkpoint from MongoDB"""
        try:
            latest_model = await GlobalModelOperations.get_latest_model()
            if latest_model:
                checkpoint_path = latest_model['model_path']
                if Path(checkpoint_path).exists():
                    checkpoint = torch.load(checkpoint_path)
                    self.model.load_state_dict(checkpoint['model_state'])
                    self.current_round = latest_model['round']
                    logger.info(f"Loaded checkpoint from round {self.current_round}")
        except Exception as e:
            logger.error(f"Error loading checkpoint: {str(e)}")

    async def start_training_round(self):
        """Initialize a new training round"""
        if self.training_in_progress:
            raise RuntimeError("Training round already in progress")
            
        self.training_in_progress = True
        self.current_round += 1
        self.client_updates.clear()
        
        logger.info(f"Starting training round {self.current_round}")
        return {"round": self.current_round}

    async def add_client_update(self, client_id: str, update: Dict):
        """Process a client's update in the current round"""
        if not self.training_in_progress:
            raise RuntimeError("No training round in progress")

        try:
            # Validate update format
            required_keys = ['model_update', 'metrics']
            if not all(key in update for key in required_keys):
                raise ValueError("Invalid update format")

            # Store client update
            self.client_updates[client_id] = update
            
            # Save client metrics to database
            metrics_data = {
                "client_id": client_id,
                "round": self.current_round,
                "metrics": update['metrics'],
                "timestamp": datetime.utcnow()
            }
            await TrainingMetricsOperations.save_metrics(metrics_data)

            # Check if we have enough updates to aggregate
            if len(self.client_updates) >= self.min_clients * self.aggregation_threshold:
                await self.aggregate_updates()
                
            return {
                "success": True,
                "round": self.current_round,
                "updates_received": len(self.client_updates)
            }

        except Exception as e:
            logger.error(f"Error processing client update: {str(e)}")
            raise

    async def aggregate_updates(self):
        """Aggregate updates from multiple clients using FedAvg algorithm"""
        logger.info("Starting model aggregation")
        
        try:
            # Initialize aggregated state dict
            aggregated_state = {}
            for key in self.model.state_dict().keys():
                aggregated_state[key] = torch.zeros_like(self.model.state_dict()[key])

            # Calculate total number of samples across all clients
            total_samples = sum(
                update['metrics']['total_samples'] 
                for update in self.client_updates.values()
            )

            # Weighted average of model parameters
            for client_id, update in self.client_updates.items():
                weight = update['metrics']['total_samples'] / total_samples
                state_dict = update['model_update']
                
                for key in state_dict:
                    if key in aggregated_state:
                        aggregated_state[key] += state_dict[key] * weight

            # Update global model
            self.model.load_state_dict(aggregated_state)

            # Save checkpoint
            await self._save_checkpoint(aggregated_state)

            # Update global metrics
            await self._update_global_metrics()

            # Reset for next round
            self.training_in_progress = False
            self.client_updates.clear()

            logger.info(f"Successfully completed round {self.current_round}")
            return {"success": True, "round": self.current_round}

        except Exception as e:
            logger.error(f"Error during aggregation: {str(e)}")
            self.training_in_progress = False
            raise

    async def _save_checkpoint(self, model_state: Dict):
        """Save model checkpoint and update database"""
        checkpoint_path = self.checkpoint_dir / f"model_round_{self.current_round}.pt"
        
        # Save model file
        torch.save({
            'round': self.current_round,
            'model_state': model_state,
            'timestamp': datetime.utcnow().isoformat()
        }, checkpoint_path)

        # Update database
        model_data = {
            "round": self.current_round,
            "model_path": str(checkpoint_path),
            "metrics": await self._get_current_metrics()
        }
        await GlobalModelOperations.save_model(model_data)

    async def _update_global_metrics(self):
        """Update global metrics after aggregation"""
        metrics = {
            "round": self.current_round,
            "clients_participated": len(self.client_updates),
            "average_accuracy": sum(
                update['metrics'].get('accuracy', 0) 
                for update in self.client_updates.values()
            ) / len(self.client_updates),
            "timestamp": datetime.utcnow()
        }
        await TrainingMetricsOperations.save_metrics(metrics)

    async def _get_current_metrics(self) -> Dict:
        """Get current training metrics"""
        return {
            "round": self.current_round,
            "participants": len(self.client_updates),
            "timestamp": datetime.utcnow().isoformat()
        }

    async def get_model_for_client(self, client_id: str) -> Dict:
        """Provide current model parameters to a client"""
        return {
            "model_state": self.model.state_dict(),
            "round": self.current_round
        }

    async def process_image(self, 
                          image_data: bytes, 
                          image_type: str,
                          patient_info: Dict) -> Dict:
        """Process a single medical image"""
        try:
            # Create upload record
            upload_data = {
                "patient_id": patient_info['id'],
                "image_type": image_type,
                "status": "processing"
            }
            upload_id = await ImageUploadOperations.create_upload(upload_data)

            # Preprocess image
            processed_image = self._preprocess_image(image_data, image_type)
            processed_image = processed_image.unsqueeze(0)  # Add batch dimension

            # Run inference
            self.model.eval()
            with torch.no_grad():
                outputs = self.model(processed_image, modality=image_type)

            # Process results
            results = self._process_results(outputs, image_type)

            # Update upload record with results
            await ImageUploadOperations.update_analysis_result(upload_id, results)

            return {
                "success": True,
                "results": results,
                "upload_id": upload_id
            }

        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            if upload_id:
                await ImageUploadOperations.update_analysis_result(
                    upload_id, 
                    {"status": "failed", "error": str(e)}
                )
            raise

    def _preprocess_image(self, image_data: bytes, image_type: str) -> torch.Tensor:
        """Preprocess image based on modality"""
        # Implementation depends on image format and requirements
        pass

    def _process_results(self, outputs: Dict, image_type: str) -> Dict:
        """Process model outputs into meaningful results"""
        classification = outputs['classification']
        segmentation = outputs['segmentation']
        
        probs = torch.softmax(classification, dim=1)
        confidence, prediction = torch.max(probs, dim=1)
        
        return {
            "prediction": prediction.item(),
            "confidence": confidence.item(),
            "segmentation": segmentation.cpu().numpy().tolist(),
            "diagnosis": self._get_diagnosis(prediction.item(), image_type),
            "timestamp": datetime.utcnow().isoformat()
        }

    def _get_diagnosis(self, prediction: int, image_type: str) -> str:
        """Convert model prediction to human-readable diagnosis"""
        diagnoses = {
            'ct': {
                0: 'Normal',
                1: 'Pneumonia',
                2: 'COVID-19',
                3: 'Lung Cancer'
            },
            'mri': {
                0: 'Normal',
                1: 'Tumor - Grade I/II',
                2: 'Tumor - Grade III/IV',
                3: 'Multiple Sclerosis'
            }
        }
        return diagnoses[image_type].get(prediction, "Unknown")

    async def get_dashboard_metrics(self) -> Dict:
        """Get metrics for dashboard display"""
        return await MetricsAggregator.get_dashboard_metrics()