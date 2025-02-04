import asyncio
import logging
from typing import List, Dict, Set
import random
from datetime import datetime
import numpy as np
from .server import FederatedServer
from .db_operations import GlobalModelOperations, TrainingMetricsOperations

class FederatedOrchestrator:
    def __init__(
        self,
        min_clients: int = 3,
        selection_fraction: float = 0.8,
        rounds: int = 100,
        timeout: int = 300  # 5 minutes timeout
    ):
        self.min_clients = min_clients
        self.selection_fraction = selection_fraction
        self.total_rounds = rounds
        self.timeout = timeout
        self.fl_server = FederatedServer(min_clients=min_clients)
        self.active_clients: Set[str] = set()
        self.round_in_progress = False

    async def register_client(self, client_id: str, client_info: Dict) -> Dict:
        """Register a new client for training"""
        self.active_clients.add(client_id)
        logging.info(f"Client {client_id} registered. Total clients: {len(self.active_clients)}")
        return {
            'success': True,
            'client_id': client_id,
            'total_clients': len(self.active_clients)
        }

    async def select_clients(self) -> List[str]:
        """Select clients for the current round using importance sampling"""
        if len(self.active_clients) < self.min_clients:
            raise ValueError("Not enough active clients")

        num_to_select = max(
            self.min_clients,
            int(len(self.active_clients) * self.selection_fraction)
        )

        # Get client metrics from previous rounds
        client_metrics = await TrainingMetricsOperations.get_all_client_metrics()
        
        if not client_metrics:  # First round or no metrics
            return random.sample(list(self.active_clients), num_to_select)

        # Calculate selection probabilities based on data quality and contribution
        selection_weights = {}
        for client_id in self.active_clients:
            metrics = client_metrics.get(client_id, {})
            
            # Factors for client selection
            data_quality = metrics.get('validation_accuracy', 0.5)
            contribution = metrics.get('num_samples', 0) / metrics.get('total_samples', 1)
            communication = metrics.get('response_rate', 1.0)
            
            # Combined weight
            weight = 0.4 * data_quality + 0.4 * contribution + 0.2 * communication
            selection_weights[client_id] = max(0.1, weight)  # Ensure minimum chance

        # Normalize weights
        total_weight = sum(selection_weights.values())
        probs = [selection_weights[cid]/total_weight for cid in self.active_clients]

        # Select clients
        selected_clients = np.random.choice(
            list(self.active_clients),
            size=num_to_select,
            replace=False,
            p=probs
        )

        return selected_clients.tolist()

    async def start_training_round(self) -> Dict:
        """Start a new training round"""
        if self.round_in_progress:
            return {'success': False, 'error': 'Round already in progress'}

        try:
            self.round_in_progress = True
            selected_clients = await self.select_clients()
            round_info = await self.fl_server.start_training_round()

            return {
                'success': True,
                'round': round_info['round'],
                'selected_clients': selected_clients,
                'timeout': self.timeout
            }

        except Exception as e:
            logging.error(f"Error starting training round: {str(e)}")
            self.round_in_progress = False
            return {'success': False, 'error': str(e)}

    async def process_client_update(self, client_id: str, update: Dict) -> Dict:
        """Process update from a client"""
        if not self.round_in_progress:
            return {'success': False, 'error': 'No active training round'}

        try:
            result = await self.fl_server.add_client_update(client_id, update)
            
            if result.get('aggregation_completed', False):
                self.round_in_progress = False

            return {
                'success': True,
                'result': result
            }

        except Exception as e:
            logging.error(f"Error processing client update: {str(e)}")
            return {'success': False, 'error': str(e)}

    async def check_round_completion(self) -> Dict:
        """Check if current round is complete"""
        if not self.round_in_progress:
            return {'status': 'no_round'}

        completion_status = await self.fl_server.check_round_completion()
        return {
            'status': 'complete' if completion_status else 'in_progress',
            'current_round': self.fl_server.current_round,
            'updates_received': len(self.fl_server.client_updates)
        }

    async def get_training_status(self) -> Dict:
        """Get current training status for dashboard"""
        return {
            'total_rounds': self.total_rounds,
            'current_round': self.fl_server.current_round,
            'active_clients': len(self.active_clients),
            'round_in_progress': self.round_in_progress,
            'global_metrics': await self.fl_server.get_training_metrics(),
            'timestamp': datetime.now().isoformat()
        }