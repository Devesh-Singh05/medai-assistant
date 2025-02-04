import torch
from torch.utils.data import DataLoader
import numpy as np
from typing import Dict, List, Optional
import logging
import asyncio
from pathlib import Path
from datetime import datetime
from .training import MedicalTrainer
from .data_preprocessing import LIDCDataset, BraTSDataset
from .model import DualTaskMedicalModel

class FederatedTrainingManager:
    def __init__(
        self,
        client_id: str,
        data_path: Dict[str, str],
        server_url: str,
        config: Dict = None
    ):
        self.client_id = client_id
        self.data_path = data_path
        self.server_url = server_url
        self.config = config or self._get_default_config()
        
        # Initialize model and trainer
        self.model = DualTaskMedicalModel()
        self.trainer = MedicalTrainer(self.model, config=self.config)
        
        # Initialize datasets
        self.datasets = self._initialize_datasets()
        
        # Training state
        self.current_round = 0
        self.training_history = []

    def _get_default_config(self) -> Dict:
        return {
            'num_local_epochs': 5,
            'batch_size': 16,
            'learning_rate': 1e-4,
            'weight_decay': 1e-5,
            'client_selection_rate': 0.8,
            'min_samples_per_client': 100,
            'privacy': {
                'noise_multiplier': 0.1,
                'max_grad_norm': 1.0
            }
        }

    def _initialize_datasets(self) -> Dict:
        """Initialize datasets for both modalities"""
        datasets = {}
        
        # LIDC-IDRI dataset for CT scans
        if 'ct' in self.data_path:
            datasets['ct'] = {
                'train': LIDCDataset(
                    self.data_path['ct'],
                    train=True
                ),
                'val': LIDCDataset(
                    self.data_path['ct'],
                    train=False
                )
            }
        
        # BraTS dataset for MRI
        if 'mri' in self.data_path:
            datasets['mri'] = {
                'train': BraTSDataset(
                    self.data_path['mri'],
                    train=True
                ),
                'val': BraTSDataset(
                    self.data_path['mri'],
                    train=False
                )
            }
        
        return datasets

    def _create_data_loaders(self) -> Dict:
        """Create data loaders for training"""
        loaders = {}
        for modality, dataset in self.datasets.items():
            loaders[modality] = {
                'train': DataLoader(
                    dataset['train'],
                    batch_size=self.config['batch_size'],
                    shuffle=True,
                    num_workers=4,
                    pin_memory=True
                ),
                'val': DataLoader(
                    dataset['val'],
                    batch_size=self.config['batch_size'],
                    shuffle=False,
                    num_workers=4,
                    pin_memory=True
                )
            }
        return loaders

    async def participate_in_round(self, round_num: int) -> Dict:
        """Participate in a federated learning round"""
        self.current_round = round_num
        metrics = {
            'ct': {'train': {}, 'val': {}},
            'mri': {'train': {}, 'val': {}}
        }
        
        try:
            # Get latest global model from server
            await self._get_global_model()
            
            # Create data loaders
            loaders = self._create_data_loaders()
            
            # Train on each modality
            for modality, loader in loaders.items():
                # Local training
                train_metrics = await self._train_modality(
                    modality,
                    loader['train'],
                    loader['val']
                )
                metrics[modality] = train_metrics
            
            # Prepare and send update to server
            update = self._prepare_client_update(metrics)
            await self._send_update_to_server(update)
            
            return {
                'success': True,
                'metrics': metrics
            }
            
        except Exception as e:
            logging.error(f"Error in training round: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    async def _train_modality(
        self,
        modality: str,
        train_loader: DataLoader,
        val_loader: DataLoader
    ) -> Dict:
        """Train on specific modality"""
        metrics = {
            'train': {},
            'val': {}
        }
        
        # Training
        for epoch in range(self.config['num_local_epochs']):
            train_metrics = self.trainer.train_epoch(
                train_loader,
                modality,
                epoch
            )
            metrics['train'][f'epoch_{epoch}'] = train_metrics
            
            # Validation
            if epoch % 2 == 0:  # Validate every 2 epochs
                val_metrics = self.trainer.validate(
                    val_loader,
                    modality
                )
                metrics['val'][f'epoch_{epoch}'] = val_metrics
        
        return metrics

    def _prepare_client_update(self, metrics: Dict) -> Dict:
        """Prepare client update for server"""
        return {
            'client_id': self.client_id,
            'round': self.current_round,
            'model_update': self.trainer.get_model_update(),
            'metrics': metrics,
            'timestamp': datetime.utcnow().isoformat(),
            'num_samples': {
                modality: len(dataset['train']) 
                for modality, dataset in self.datasets.items()
            }
        }

    async def _get_global_model(self):
        """Get global model from server"""
        # Implement the API call to get global model
        pass

    async def _send_update_to_server(self, update: Dict):
        """Send update to server"""
        # Implement the API call to send update
        pass

    def save_checkpoint(self, path: str):
        """Save client checkpoint"""
        checkpoint = {
            'round': self.current_round,
            'model_state': self.model.state_dict(),
            'optimizer_state': self.trainer.optimizer.state_dict(),
            'config': self.config,
            'training_history': self.training_history
        }
        torch.save(checkpoint, path)

    def load_checkpoint(self, path: str):
        """Load client checkpoint"""
        checkpoint = torch.load(path)
        self.current_round = checkpoint['round']
        self.model.load_state_dict(checkpoint['model_state'])
        self.trainer.optimizer.load_state_dict(checkpoint['optimizer_state'])
        self.config = checkpoint['config']
        self.training_history = checkpoint['training_history']