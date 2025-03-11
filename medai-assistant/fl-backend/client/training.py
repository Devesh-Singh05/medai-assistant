import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import numpy as np
from typing import Dict, List, Optional
import logging
from pathlib import Path
from .model import DualTaskMedicalModel
from .data_preprocessing import LIDCDataset, BraTSDataset
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import monai.metrics as monai_metrics

class MedicalTrainer:
    def __init__(
        self,
        model: DualTaskMedicalModel,
        device: str = 'cuda' if torch.cuda.is_available() else 'cpu',
        config: Dict = None
    ):
        self.model = model.to(device)
        self.device = device
        self.config = config or self.get_default_config()
        
        # Initialize optimizers
        self.optimizer = optim.Adam(
            self.model.parameters(),
            lr=self.config['learning_rate'],
            weight_decay=self.config['weight_decay']
        )
        
        # Initialize loss functions
        self.classification_loss = nn.CrossEntropyLoss()
        self.segmentation_loss = nn.BCEWithLogitsLoss()
        
        # Initialize metrics
        self.dice_metric = monai_metrics.DiceMetric(
            include_background=False,
            reduction="mean"
        )

    @staticmethod
    def get_default_config():
        return {
            'learning_rate': 1e-4,
            'weight_decay': 1e-5,
            'batch_size': 16,
            'num_epochs': 5,
            'validation_interval': 100,
            'classification_weight': 0.5,
            'segmentation_weight': 0.5
        }

    def train_epoch(
        self,
        train_loader: DataLoader,
        modality: str,
        epoch: int
    ) -> Dict:
        """Train for one epoch"""
        self.model.train()
        total_loss = 0
        metrics = {
            'classification_accuracy': [],
            'dice_scores': [],
            'batch_losses': []
        }

        for batch_idx, batch in enumerate(train_loader):
            # Move data to device
            images = batch['image'].to(self.device)
            if modality == 'mri':
                images = torch.cat([
                    batch['images'][mod].to(self.device) 
                    for mod in ['t1', 't1ce', 't2', 'flair']
                ], dim=1)
            
            masks = batch['mask'].to(self.device) if 'mask' in batch else None
            labels = batch.get('label')
            
            if labels is not None:
                labels = labels.to(self.device)

            # Forward pass
            self.optimizer.zero_grad()
            outputs = self.model(images, modality=modality)
            
            # Calculate losses
            loss = 0
            if labels is not None:
                class_loss = self.classification_loss(
                    outputs['classification'],
                    labels
                )
                loss += self.config['classification_weight'] * class_loss
                
                # Update classification metrics
                pred = outputs['classification'].argmax(dim=1)
                accuracy = (pred == labels).float().mean()
                metrics['classification_accuracy'].append(accuracy.item())

            if masks is not None and outputs['segmentation'] is not None:
                seg_loss = self.segmentation_loss(
                    outputs['segmentation'],
                    masks
                )
                loss += self.config['segmentation_weight'] * seg_loss
                
                # Calculate Dice score
                dice_score = self.dice_metric(
                    outputs['segmentation'].sigmoid() > 0.5,
                    masks
                )
                metrics['dice_scores'].append(dice_score.item())

            # Backward pass
            loss.backward()
            
            # Add differential privacy noise
            self.model.add_noise(noise_scale=0.001)
            
            self.optimizer.step()
            
            total_loss += loss.item()
            metrics['batch_losses'].append(loss.item())

            # Log progress
            if batch_idx % 10 == 0:
                logging.info(f'Train Epoch: {epoch} [{batch_idx}/{len(train_loader)} '
                           f'Loss: {loss.item():.6f}]')

        # Calculate epoch metrics
        epoch_metrics = {
            'loss': total_loss / len(train_loader),
            'classification_accuracy': np.mean(metrics['classification_accuracy']) if metrics['classification_accuracy'] else 0,
            'mean_dice_score': np.mean(metrics['dice_scores']) if metrics['dice_scores'] else 0
        }

        return epoch_metrics

    @torch.no_grad()
    def validate(
        self,
        val_loader: DataLoader,
        modality: str
    ) -> Dict:
        """Validate the model"""
        self.model.eval()
        val_loss = 0
        metrics = {
            'classification_accuracy': [],
            'dice_scores': [],
            'predictions': [],
            'true_labels': []
        }

        for batch in val_loader:
            # Process batch similar to training
            images = batch['image'].to(self.device)
            if modality == 'mri':
                images = torch.cat([
                    batch['images'][mod].to(self.device) 
                    for mod in ['t1', 't1ce', 't2', 'flair']
                ], dim=1)
            
            masks = batch['mask'].to(self.device) if 'mask' in batch else None
            labels = batch.get('label')
            
            if labels is not None:
                labels = labels.to(self.device)

            outputs = self.model(images, modality=modality)
            
            # Calculate metrics
            if labels is not None:
                pred = outputs['classification'].argmax(dim=1)
                metrics['predictions'].extend(pred.cpu().numpy())
                metrics['true_labels'].extend(labels.cpu().numpy())

            if masks is not None and outputs['segmentation'] is not None:
                dice_score = self.dice_metric(
                    outputs['segmentation'].sigmoid() > 0.5,
                    masks
                )
                metrics['dice_scores'].append(dice_score.item())

        # Calculate final metrics
        if metrics['predictions']:
            precision, recall, f1, _ = precision_recall_fscore_support(
                metrics['true_labels'],
                metrics['predictions'],
                average='weighted'
            )
        else:
            precision = recall = f1 = 0

        validation_metrics = {
            'accuracy': accuracy_score(
                metrics['true_labels'],
                metrics['predictions']
            ) if metrics['predictions'] else 0,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'mean_dice_score': np.mean(metrics['dice_scores']) if metrics['dice_scores'] else 0
        }

        return validation_metrics

    def get_model_update(self) -> Dict:
        """Get model parameters for federated learning"""
        return {
            'model_state': self.model.state_dict(),
            'optimizer_state': self.optimizer.state_dict()
        }

    def set_model_update(self, update: Dict):
        """Update model with new parameters"""
        self.model.load_state_dict(update['model_state'])
        if 'optimizer_state' in update:
            self.optimizer.load_state_dict(update['optimizer_state'])