import json
import logging
from pathlib import Path
from typing import Dict, List
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

class MetricsLogger:
    def __init__(self, log_dir: str, client_id: str):
        """Initialize metrics logger"""
        self.log_dir = Path(log_dir)
        self.client_id = client_id
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup files
        self.metrics_file = self.log_dir / f"{client_id}_metrics.json"
        self.training_log = self.log_dir / f"{client_id}_training.log"
        
        # Initialize logging
        self._setup_logging()
        
        # Load or initialize metrics history
        self.metrics_history = self._load_metrics_history()

    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            filename=self.training_log,
            format='%(asctime)s - %(levelname)s - %(message)s',
            level=logging.INFO
        )

    def _load_metrics_history(self) -> List[Dict]:
        """Load existing metrics history or initialize new one"""
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logging.warning("Could not load existing metrics. Starting fresh.")
        return []

    def log_training_metrics(self, round_num: int, metrics: Dict):
        """Log metrics for a training round"""
        record = {
            'round': round_num,
            'timestamp': datetime.now().isoformat(),
            'metrics': {
                'ct': self._format_modality_metrics(metrics.get('ct', {})),
                'mri': self._format_modality_metrics(metrics.get('mri', {}))
            }
        }
        
        self.metrics_history.append(record)
        self._save_metrics()
        self._log_round_summary(round_num, metrics)

    def _format_modality_metrics(self, modality_metrics: Dict) -> Dict:
        """Format metrics for a single modality"""
        if not modality_metrics:
            return {}
            
        formatted = {}
        for phase in ['train', 'val']:
            if phase in modality_metrics:
                formatted[phase] = {
                    'loss': modality_metrics[phase].get('loss', 0),
                    'accuracy': modality_metrics[phase].get('accuracy', 0),
                    'dice_score': modality_metrics[phase].get('dice_score', 0)
                }
        return formatted

    def _save_metrics(self):
        """Save metrics to file"""
        with open(self.metrics_file, 'w') as f:
            json.dump(self.metrics_history, f, indent=2)

    def _log_round_summary(self, round_num: int, metrics: Dict):
        """Log summary of the training round"""
        summary = f"\nRound {round_num} Summary:\n"
        
        for modality in ['ct', 'mri']:
            if modality in metrics:
                mod_metrics = metrics[modality]
                summary += f"\n{modality.upper()}:\n"
                
                if 'train' in mod_metrics:
                    train = mod_metrics['train']
                    summary += f"Training - "
                    summary += f"Loss: {train.get('loss', 0):.4f}, "
                    summary += f"Accuracy: {train.get('accuracy', 0):.4f}, "
                    summary += f"Dice: {train.get('dice_score', 0):.4f}\n"
                
                if 'val' in mod_metrics:
                    val = mod_metrics['val']
                    summary += f"Validation - "
                    summary += f"Loss: {val.get('loss', 0):.4f}, "
                    summary += f"Accuracy: {val.get('accuracy', 0):.4f}, "
                    summary += f"Dice: {val.get('dice_score', 0):.4f}\n"
        
        logging.info(summary)

    def get_training_metrics(self) -> Dict:
        """Get latest training metrics for dashboard"""
        if not self.metrics_history:
            return {
                'ct': {'accuracy': 0, 'dice_score': 0},
                'mri': {'accuracy': 0, 'dice_score': 0},
                'round': 0
            }
            
        latest = self.metrics_history[-1]
        return {
            'ct': {
                'accuracy': latest['metrics']['ct'].get('val', {}).get('accuracy', 0),
                'dice_score': latest['metrics']['ct'].get('val', {}).get('dice_score', 0)
            },
            'mri': {
                'accuracy': latest['metrics']['mri'].get('val', {}).get('accuracy', 0),
                'dice_score': latest['metrics']['mri'].get('val', {}).get('dice_score', 0)
            },
            'round': latest['round']
        }

    def plot_metrics(self, save_path: str = None):
        """Plot training metrics"""
        if not self.metrics_history:
            return

        # Prepare data for plotting
        rounds = []
        ct_acc = []
        ct_dice = []
        mri_acc = []
        mri_dice = []

        for record in self.metrics_history:
            rounds.append(record['round'])
            ct_metrics = record['metrics']['ct'].get('val', {})
            mri_metrics = record['metrics']['mri'].get('val', {})
            
            ct_acc.append(ct_metrics.get('accuracy', 0))
            ct_dice.append(ct_metrics.get('dice_score', 0))
            mri_acc.append(mri_metrics.get('accuracy', 0))
            mri_dice.append(mri_metrics.get('dice_score', 0))

        # Create plots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))

        # Accuracy plot
        ax1.plot(rounds, ct_acc, label='CT Accuracy')
        ax1.plot(rounds, mri_acc, label='MRI Accuracy')
        ax1.set_title('Validation Accuracy')
        ax1.set_xlabel('Round')
        ax1.set_ylabel('Accuracy')
        ax1.legend()
        ax1.grid(True)

        # Dice score plot
        ax2.plot(rounds, ct_dice, label='CT Dice Score')
        ax2.plot(rounds, mri_dice, label='MRI Dice Score')
        ax2.set_title('Validation Dice Score')
        ax2.set_xlabel('Round')
        ax2.set_ylabel('Dice Score')
        ax2.legend()
        ax2.grid(True)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path)
            plt.close()
        else:
            plt.show()