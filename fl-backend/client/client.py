import torch
import torch.nn as nn
import torch.optim as optim
from typing import Dict, List, Optional
import logging
from datetime import datetime
from model import MedAIModel
from data_loader import get_data_loaders, PatientDataManager
import asyncio
import requests
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FederatedClient:
    def __init__(
        self,
        client_id: str,
        server_url: str,
        data_path: str,
        device: str = 'cuda' if torch.cuda.is_available() else 'cpu'
    ):
        self.client_id = client_id
        self.server_url = server_url
        self.device = device
        self.model = MedAIModel().to(device)
        self.optimizer = optim.Adam(self.model.parameters())
        self.patient_manager = PatientDataManager(data_path)
        
        # Training data loaders
        self.train_loader = get_data_loaders(data_path)
        
        # Metrics tracking
        self.metrics = {
            'uploads_this_week': 0,
            'analyses_completed': 0,
            'accuracy_rate': 0.0,
            'recent_uploads': []
        }

    async def train_round(self) -> Dict:
        """Perform one round of federated training"""
        self.model.train()
        total_loss = 0
        correct = 0
        total = 0

        for batch_idx, (data, target, modality) in enumerate(self.train_loader):
            data, target = data.to(self.device), target.to(self.device)
            self.optimizer.zero_grad()

            # Forward pass
            outputs = self.model(data, modality=modality)
            loss = nn.CrossEntropyLoss()(outputs['classification'], target)

            # Backward pass
            loss.backward()
            self.model.add_noise()  # Add DP noise
            self.optimizer.step()

            total_loss += loss.item()
            pred = outputs['classification'].argmax(dim=1)
            correct += pred.eq(target).sum().item()
            total += target.size(0)

        # Calculate metrics
        accuracy = (correct / total) * 100
        avg_loss = total_loss / len(self.train_loader)

        # Update local metrics
        self.metrics['accuracy_rate'] = accuracy

        return {
            'client_id': self.client_id,
            'loss': avg_loss,
            'accuracy': accuracy,
            'model_update': self.get_model_update()
        }

    async def process_image(self, 
                          image_data: bytes, 
                          image_type: str,
                          patient_info: Dict) -> Dict:
        """Process a single medical image"""
        try:
            # Save image and create record
            image_path = f"data/uploads/{patient_info['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            with open(image_path, 'wb') as f:
                f.write(image_data)

            # Preprocess image
            processed_image = self._preprocess_image(image_data, image_type)
            processed_image = processed_image.to(self.device).unsqueeze(0)

            # Run inference
            self.model.eval()
            with torch.no_grad():
                outputs = self.model(processed_image, modality=image_type)

            # Process results
            result = self._process_results(outputs, image_type)

            # Update patient records
            self.patient_manager.add_patient_record(
                patient_id=patient_info['id'],
                patient_name=patient_info['name'],
                image_path=image_path,
                image_type=image_type,
                analysis_result=result
            )

            # Update metrics
            self._update_metrics(result)

            return {
                'success': True,
                'result': result,
                'metrics': self.get_metrics()
            }

        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_model_update(self) -> Dict:
        """Get model parameters for sending to server"""
        return {
            'model_state': self.model.state_dict(),
            'metrics': self.metrics
        }

    def update_model(self, global_params: Dict):
        """Update local model with global parameters"""
        self.model.load_state_dict(global_params['model_state'])
        logger.info("Updated local model with global parameters")

    def _preprocess_image(self, image_data: bytes, image_type: str) -> torch.Tensor:
        """Preprocess image based on type"""
        # Implementation similar to data_loader.py
        pass

    def _process_results(self, outputs: Dict, image_type: str) -> Dict:
        """Process model outputs into meaningful results"""
        classification = outputs['classification']
        segmentation = outputs['segmentation']
        features = outputs['features']

        probs = torch.softmax(classification, dim=1)
        confidence, prediction = torch.max(probs, dim=1)

        return {
            'prediction': prediction.item(),
            'confidence': confidence.item(),
            'segmentation': segmentation.cpu().numpy(),
            'features': features.cpu().numpy(),
            'diagnosis': self._get_diagnosis(prediction.item(), image_type),
            'timestamp': datetime.now().isoformat()
        }

    def _get_diagnosis(self, prediction: int, image_type: str) -> str:
        """Convert prediction to human-readable diagnosis"""
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
        return diagnoses[image_type][prediction]

    def get_metrics(self) -> Dict:
        """Get current metrics for dashboard"""
        return self.metrics

    def _update_metrics(self, result: Dict):
        """Update metrics after processing an image"""
        self.metrics['uploads_this_week'] += 1
        self.metrics['analyses_completed'] += 1
        
        # Keep only recent uploads
        if len(self.metrics['recent_uploads']) >= 100:
            self.metrics['recent_uploads'].pop()
        self.metrics['recent_uploads'].insert(0, result)